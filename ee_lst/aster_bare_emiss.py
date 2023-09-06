import ee

# Load ASTER emissivity
aster = ee.Image("NASA/ASTER_GED/AG100_003")

# Calculate ASTER FVC from NDVI
aster_ndvi = aster.select('ndvi').multiply(0.01)
aster_fvc = aster_ndvi.expression(
    '((ndvi - ndvi_bg) / (ndvi_vg - ndvi_bg)) ** 2',
    {'ndvi': aster_ndvi, 'ndvi_bg': 0.2, 'ndvi_vg': 0.86}
)
aster_fvc = aster_fvc.where(aster_fvc.lt(0.0), 0.0)
aster_fvc = aster_fvc.where(aster_fvc.gt(1.0), 1.0)

def emiss_bare_band(band, image):
    """
    Calculate bare ground emissivity for a specific ASTER band.

    Parameters:
    - band (str): ASTER band name (e.g., 'emissivity_band10')
    - image (ee.Image): Input image to clip the ASTER data to its geometry

    Returns:
    - ee.Image: Bare ground emissivity of the specified band
    """
    return image.expression(
        '(EM - 0.99 * fvc) / (1.0 - fvc)',
        {
            'EM': aster.select(band).multiply(0.001),
            'fvc': aster_fvc
        }
    ).clip(image.geometry())

# Define functions for each band
def emiss_bare_band10(image):
    return emiss_bare_band('emissivity_band10', image)

def emiss_bare_band11(image):
    return emiss_bare_band('emissivity_band11', image)

def emiss_bare_band12(image):
    return emiss_bare_band('emissivity_band12', image)

def emiss_bare_band13(image):
    return emiss_bare_band('emissivity_band13', image)

def emiss_bare_band14(image):
    return emiss_bare_band('emissivity_band14', image)

# You can add more functions or utilities as needed based on the content of the original `ASTER_bare_emiss.js`.
