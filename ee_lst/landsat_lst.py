import ee
from ee_lst.ncep_tpw import add_tpw_band
from ee_lst.cloudmask import mask_sr
from ee_lst.compute_ndvi import add_ndvi_band
from ee_lst.compute_fvc import add_fvc_band
from ee_lst.compute_emissivity import add_emissivity_band
from ee_lst.smw_algorithm import add_lst_band
from ee_lst.constants import LANDSAT_BANDS


def initialize_ee():
    if not ee.data._initialized:
        try:
            ee.Initialize()
        except Exception:
            print("Please authenticate Google Earth Engine first.")
            ee.Authenticate()
            ee.Initialize()


def fetch_landsat_collection(landsat, date_start, date_end,
                             geometry, use_ndvi):
    """
    Fetches a Landsat collection based on the provided parameters
    and applies several transformations.

    Parameters:
    - landsat: Name of the Landsat collection (e.g., 'L8')
    - date_start: Start date for the collection
    - date_end: End date for the collection
    - geometry: Area of interest
    - use_ndvi: Boolean indicating whether to use NDVI

    Returns:
    - landsatLST: Processed Landsat collection with LST
    """
    # Ensure Earth Engine is initialized
    initialize_ee()

    # Check if the provided Landsat collection is valid
    if landsat not in LANDSAT_BANDS.keys():
        raise ValueError(f"Invalid Landsat constellation: {landsat}. \
            Valid options are: {list(LANDSAT_BANDS.keys())}")

    collection_dict = LANDSAT_BANDS[landsat]

    # Load TOA Radiance/Reflectance
    landsat_toa = (ee.ImageCollection(collection_dict['TOA'])
                     .filterDate(date_start, date_end)
                     .filterBounds(geometry))

    # Load Surface Reflectance collection for NDVI  and apply transformations
    landsat_sr = (ee.ImageCollection(collection_dict['SR'])
                    .filterDate(date_start, date_end)
                    .filterBounds(geometry)
                    .map(mask_sr)
                    .map(lambda image: add_ndvi_band(landsat, image))
                    .map(lambda image: add_fvc_band(landsat, image))
                    .map(add_tpw_band)
                    .map(lambda image: add_emissivity_band(landsat,
                                                           use_ndvi, image)))

    # Combine collections
    tir = collection_dict['TIR']
    visw = collection_dict['VISW'] + ['NDVI', 'FVC', 'TPW', 'TPWpos', 'EM']
    landsat_all = landsat_sr.select(visw).combine(landsat_toa.select(tir),
                                                  True)

    # Compute the LST
    landsat_lst = landsat_all.map(lambda image: add_lst_band(landsat, image))

    return landsat_lst
