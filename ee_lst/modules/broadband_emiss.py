import ee
from python_modules.ASTER_bare_emiss import (
    emiss_bare_band10,
    emiss_bare_band11,
    emiss_bare_band12,
    emiss_bare_band13,
    emiss_bare_band14
)

def add_band(dynamic, image):
    """
    Compute broad-band emissivity from ASTER GED.

    Parameters:
    - dynamic (bool): If True, use vegetation cover correction. If False, use original ASTER GED emissivity.
    - image (ee.Image): Input image to clip the ASTER data to its geometry.

    Returns:
    - ee.Image: Input image with an additional band 'BBE' for broad-band emissivity.
    """
    
    # Get ASTER emissivity
    aster = ee.Image("NASA/ASTER_GED/AG100_003").clip(image.geometry())
    
    def compute_emissivity(orig_band, emiss_bare_func):
        orig = aster.select(orig_band).multiply(0.001)
        dynam = image.expression(
            'fvc * 0.99 + (1 - fvc) * em_bare',
            {
                'fvc': image.select('FVC'),
                'em_bare': emiss_bare_func(image)
            }
        )
        return ee.Image(ee.Algorithms.If(dynamic, dynam, orig))
    
    em10 = compute_emissivity('emissivity_band10', emiss_bare_band10)
    em11 = compute_emissivity('emissivity_band11', emiss_bare_band11)
    em12 = compute_emissivity('emissivity_band12', emiss_bare_band12)
    em13 = compute_emissivity('emissivity_band13', emiss_bare_band13)
    em14 = compute_emissivity('emissivity_band14', emiss_bare_band14)
    
    bbe = image.expression(
        '0.128 + 0.014 * em10 + 0.145 * em11 + 0.241 * em12 + 0.467 * em13 + 0.004 * em14',
        {'em10': em10, 'em11': em11, 'em12': em12, 'em13': em13, 'em14': em14}
    )
    
    return image.addBands(bbe.rename('BBE'))

# You can add more functions or utilities as needed based on the content of the original `broadband_emiss.js`.
