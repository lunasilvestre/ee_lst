import ee
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from modules.landsat_lst import fetch_landsat_collection
import io
from googleapiclient.http import MediaIoBaseDownload

service_account_file = '.gee-sa-priv-key.json'
folder_name = "python_lst_geotiffs"
local_download_path = "./downloads"

SCOPES = [
    'https://www.googleapis.com/auth/earthengine',
    'https://www.googleapis.com/auth/devstorage.full_control',
    'https://www.googleapis.com/auth/drive'
]


def initialize_services(service_account_file):
    """Initialize Earth Engine and Google Drive services."""
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES)
    ee.Initialize(credentials)
    return build('drive', 'v3', credentials=credentials)


def clean_folder(service, folder_name):
    """Delete all files in the specified Google Drive folder."""

    # Search for the folder by its name
    folder_results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
        fields="files(id)"
    ).execute()

    folders = folder_results.get('files', [])

    if not folders:
        print(f"Folder {folder_name} not found.")
        return

    folder_id = folders[0]['id']

    # List all files in the folder
    file_results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()

    files = file_results.get('files', [])

    # Delete each file
    for file in files:
        try:
            service.files().delete(fileId=file['id']).execute()
            print(f"Deleted {file['name']} from {folder_name}")
        except Exception as e:
            print(f"Error deleting {file['name']} from {folder_name}: {e}")


def download_files(service, folder_name, download_path):
    """Download all files from the specified Google Drive folder to a local path."""

    # Search for the folder by its name
    folder_results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
        fields="files(id)"
    ).execute()

    folders = folder_results.get('files', [])

    if not folders:
        print(f"Folder {folder_name} not found.")
        return

    folder_id = folders[0]['id']

    # List all files in the folder
    file_results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, mimeType)"
    ).execute()

    files = file_results.get('files', [])

    # Download each file
    for file in files:
        request = service.files().get_media(fileId=file['id'])
        file_name = file['name']

        fh = io.FileIO(f"{download_path}/{file_name}", 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            msg = "Downloaded "
            msg += f"{int(status.progress() * 100)}% of {file_name}"
            print(msg)

    print(f"All files downloaded to {download_path}")


def kelvin_to_celsius(image):
    """Convert an LST image from Kelvin to Celsius."""
    return image.subtract(273.15)


def process_data(drive_service, folder_name):
    """Process and export visualizations."""
    try:
        geometry = ee.Geometry.Rectangle([-8.91, 40.0, -8.3, 40.4])
        satellite = "L8"
        date_start = "2022-05-15"
        date_end = "2022-05-31"
        use_ndvi = True

        landsat_coll = fetch_landsat_collection(
            satellite, date_start, date_end, geometry, use_ndvi)

        ex_image = landsat_coll.first()

        cmap1 = ["blue", "cyan", "green", "yellow", "red"]
        cmap2 = ["F2F2F2", "EFC2B3", "ECB176", "E9BD3A", "E6E600", "63C600", "00A600"]

        visualizations = [
            {'bands': ['TPW'], 'min': 0.0, 'max': 60.0, 'palette': cmap1,
             'description': 'TCWV'},
            {'bands': ['TPWpos'], 'min': 0.0, 'max': 9.0, 'palette': cmap1,
             'description': 'TCWVpos'},
            {'bands': ['FVC'], 'min': 0.0, 'max': 1.0, 'palette': cmap2,
             'description': 'FVC'},
            {'bands': ['EM'], 'min': 0.9, 'max': 1.0, 'palette': cmap1,
             'description': 'Emissivity'},
            {'bands': ['B10'], 'min': 290, 'max': 320, 'palette': cmap1,
             'description': 'TIR_BT'},
            {'bands': ['LST'], 'min': 290, 'max': 320, 'palette': cmap1,
             'description': 'LST'},
            {'bands': ['LST'], 'description': 'LST_Celsius_Raw'},
            {'bands': ['SR_B4', 'SR_B3', 'SR_B2'], 'min': 0, 'max': 0.3,
             'description': 'RGB'},
        ]

        for vis in visualizations:
            if 'RGB' in vis['description']:
                # Special case for RGB. We don't need to apply a palette.
                export_image = ex_image.select(vis['bands'])
            elif vis['description'] == 'LST_Celsius_Raw':
                # Special case for raw LST in Celsius.
                export_image = kelvin_to_celsius(ex_image.select(vis['bands']))
            else:
                export_image = ex_image.visualize(
                    bands=vis['bands'],
                    min=vis['min'],
                    max=vis['max'],
                    palette=vis['palette']
                )

            export_params = {
                'image': export_image,
                'description': vis['description'],
                'scale': 30,
                'region': geometry.getInfo()['coordinates'],
                'fileFormat': 'GeoTIFF',
                'folder': folder_name,
                'crs': 'EPSG:4326',
                'formatOptions': {
                    'cloudOptimized': True
                }
            }

            task = ee.batch.Export.image.toDrive(**export_params)
            task.start()

            while task.status()['state'] in ['READY', 'RUNNING']:
                print('Task status:', task.status())
                time.sleep(30)

            print('Task completed with state:', task.status()['state'])
    except Exception as e:
        print(f"Error processing and exporting data: {e}")


if __name__ == "__main__":
    drive_service = initialize_services(service_account_file)

    # Clean the folder in Google Drive
    clean_folder(drive_service, folder_name)

    process_data(drive_service, folder_name)

    # Download files to the container
    download_files(drive_service, folder_name, local_download_path)
