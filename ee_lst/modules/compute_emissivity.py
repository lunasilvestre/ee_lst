import ee
from python_modules import ASTER_bare_emiss

def add_band(landsat, use_ndvi, image):
    """
    Compute surface emissivity for a given Landsat image using ASTER and FVC.

    Parameters:
    - landsat (str): ID of the Landsat satellite (e.g., 'L8')
    - use_ndvi (bool): If True, NDVI values are used to obtain a dynamic emissivity; 
                       if False, emissivity is obtained directly from ASTER
    - image (ee.Image): Input Landsat image with FVC band

    Returns:
    - ee.Image: Image with added EM band
    """
    
    c13 = {
        'L4': 0.3222,
        'L5': -0.0723,
        'L7': 0.2147,
        'L8': 0.6820
    }.get(landsat, 0.6820)  # Default to L8 if not found
    
    c14 = {
        'L4': 0.6498,
        'L5': 1.0521,
        'L7': 0.7789,
        'L8': 0.2578
    }.get(landsat, 0.2578)  # Default to L8 if not found
    
    c = {
        'L4': 0.0272,
        'L5': 0.0195,
        'L7': 0.0059,
        'L8': 0.0584
    }.get(landsat, 0.0584)  # Default to L8 if not found
    
    # Get ASTER emissivity and convolve to Landsat band
    emiss_bare = image.expression(
        'c13 * EM13 + c14 * EM14 + c',
        {
            'EM13': ASTER_bare_emiss.emiss_bare_band13(image),
            'EM14': ASTER_bare_emiss.emiss_bare_band14(image),
            'c13': ee.Image(c13),
            'c14': ee.Image(c14),
            'c': ee.Image(c)
        }
    )
    
    # Compute the dynamic emissivity for Landsat
    EMd = image.expression(
        'fvc * 0.99 + (1 - fvc) * em_bare',
        {
            'fvc': image.select('FVC'),
            'em_bare': emiss_bare
        }
    )
    
    # Compute emissivity directly from ASTER without vegetation correction
    aster = ee.Image("NASA/ASTER_GED/AG100_003").clip(image.geometry())
    EM0 = image.expression(
        'c13 * EM13 + c14 * EM14 + c',
        {
            'EM13': aster.select('emissivity_band13').multiply(0.001),
            'EM14': aster.select('emissivity_band14').multiply(0.001),
            'c13': ee.Image(c13),
            'c14': ee.Image(c14),
            'c': ee.Image(c)
        }
    )
    
    # Select which emissivity to output based on user selection
    EM = EMd if use_ndvi else EM0
    
    # Prescribe emissivity of water and snow/ice bodies
    qa = image.select('QA_PIXEL')
    EM = EM.where(qa.bitwiseAnd(1 << 7), 0.99)
    EM = EM.where(qa.bitwiseAnd(1 << 5), 0.989)
    
    return image.addBands(EM.rename('EM'))

# You can add more functions as needed based on the content of the original `compute_emissivity.js`.
