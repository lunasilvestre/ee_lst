import ee

# Trigger the authentication flow.
ee.Authenticate()

# Initialize the library.
ee.Initialize()

# Import required modules (these would be other refactored Python files)
from python_modules.NCEP_TPW import add_band as add_TPW
from python_modules.cloudmask import sr as cloud_mask
from python_modules.compute_NDVI import add_band as add_NDVI
from python_modules.compute_FVC import add_band as add_FVC
from python_modules.compute_emissivity import add_band as add_emissivity
from python_modules.SMWalgorithm import add_band as add_LST

COLLECTION = {
    'L4': {
        'TOA': 'LANDSAT/LT04/C02/T1_TOA',
        'SR': 'LANDSAT/LT04/C02/T1_L2',
        'TIR': ['B6'],
        'VISW': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL']
    },
    'L5': {
        'TOA': 'LANDSAT/LT05/C02/T1_TOA',
        'SR': 'LANDSAT/LT05/C02/T1_L2',
        'TIR': ['B6',],
        'VISW': ['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B7','QA_PIXEL']
    },
    'L7': {
        'TOA': 'LANDSAT/LE07/C02/T1_TOA',
        'SR': 'LANDSAT/LE07/C02/T1_L2',
        'TIR': ['B6_VCID_1','B6_VCID_2'],
        'VISW': ['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B7','QA_PIXEL']
    },
    'L8': {
        'TOA': 'LANDSAT/LC08/C02/T1_TOA',
        'SR': 'LANDSAT/LC08/C02/T1_L2',
        'TIR': ['B10','B11'],
        'VISW': ['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7','QA_PIXEL']
    },
    'L9': {
        'TOA': 'LANDSAT/LC09/C02/T1_TOA',
        'SR': 'LANDSAT/LC09/C02/T1_L2',
        'TIR': ['B10','B11'],
        'VISW': ['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7','QA_PIXEL']
    }
}

def collection(landsat, date_start, date_end, geometry, use_ndvi):
    collection_dict = COLLECTION[landsat]

    # Load TOA Radiance/Reflectance
    landsatTOA = ee.ImageCollection(collection_dict['TOA']).filterDate(date_start, date_end).filterBounds(geometry)
    
    # Load Surface Reflectance collection for NDVI
    landsatSR = (ee.ImageCollection(collection_dict['SR'])
                 .filterDate(date_start, date_end)
                 .filterBounds(geometry)
                 .map(cloud_mask)
                 .map(lambda image: add_NDVI(landsat, image))
                 .map(lambda image: add_FVC(landsat, image))
                 .map(add_TPW)
                 .map(lambda image: add_emissivity(landsat, use_ndvi, image)))

    # Combine collections
    tir = collection_dict['TIR']
    visw = collection_dict['VISW'] + ['NDVI', 'FVC', 'TPW', 'TPWpos', 'EM']
    landsatALL = landsatSR.select(visw).combine(landsatTOA.select(tir), True)
    
    # Compute the LST
    landsatLST = landsatALL.map(lambda image: add_LST(landsat, image))

    return landsatLST
