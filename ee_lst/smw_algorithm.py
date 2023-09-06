import ee
from ee_lst.constants import SMW_COEFFICIENTS, LANDSAT_BANDS

def add_lst_band(landsat, image):
    """
    Apply the Statistical Mono-Window algorithm to compute the LST.

    Parameters:
    - landsat (str): ID of the Landsat satellite (e.g., 'L8')
    - image (ee.Image): Input Landsat image

    Returns:
    - ee.Image: Image with added LST band
    """
    
    # Check for valid Landsat version
    if landsat not in LANDSAT_BANDS:
        raise ValueError(f"Invalid Landsat version provided: {landsat}. Supported versions are: {', '.join(LANDSAT_BANDS.keys())}.")
    
    # Check for required image bands
    required_bands = ['EM', 'TPW'] + LANDSAT_BANDS[landsat]['TIR']
    missing_bands = [band for band in required_bands if band not in image.bandNames().getInfo()]
    if missing_bands:
        raise ValueError(f"Missing required bands in the image: {', '.join(missing_bands)}.")

    # Directly access the coefficients for the given Landsat version
    coeff = SMW_COEFFICIENTS.get(landsat)
    if not coeff:
        raise ValueError(f"Missing coefficients for Landsat version: {landsat}.")
    
    A_img = ee.Image.constant(coeff['A'])
    B_img = ee.Image.constant(coeff['B'])
    C_img = ee.Image.constant(coeff['C'])
    
    # Directly access the TIR band from the LANDSAT_BANDS dictionary
    tir = LANDSAT_BANDS[landsat]['TIR'][0]
    
    lst = image.expression(
        'A * Tb1 / em1 + B / em1 + C',
        {
            'A': A_img,
            'B': B_img,
            'C': C_img,
            'em1': image.select('EM'),
            'Tb1': image.select(tir)
        }
    ).updateMask(image.select('TPW').lt(0).Not())
    
    return image.addBands(lst.rename('LST'))
