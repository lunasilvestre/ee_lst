import ee
from ee_lst.constants import SMW_COEFFICIENTS, LANDSAT_BANDS

def get_lookup_table(coeff, prop_1, prop_2):
    """
    Create a lookup between two columns in a list of dictionaries.
    """
    prop_1_list = [item[prop_1] for item in coeff]
    prop_2_list = [item[prop_2] for item in coeff]
    return prop_1_list, prop_2_list

def add_lst_band(landsat, image):
    """
    Apply the Statistical Mono-Window algorithm to compute the LST.

    Parameters:
    - landsat (str): ID of the Landsat satellite (e.g., 'L8')
    - image (ee.Image): Input Landsat image

    Returns:
    - ee.Image: Image with added LST band
    """
    
    # Select algorithm coefficients
    coeff_SMW = SMW_COEFFICIENTS.get(landsat, SMW_COEFFICIENTS['L9'])  # Default to L9 if not found
    
    # Create lookups for the algorithm coefficients
    A_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'A')
    B_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'B')
    C_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'C')
  
    # Map coefficients to the image using the TPW bin position
    A_img = image.remap(A_lookup[0], A_lookup[1], 0.0, 'TPWpos').resample('bilinear')
    B_img = image.remap(B_lookup[0], B_lookup[1], 0.0, 'TPWpos').resample('bilinear')
    C_img = image.remap(C_lookup[0], C_lookup[1], 0.0, 'TPWpos').resample('bilinear')
    
    # Select TIR band
    tir = LANDSAT_BANDS[landsat]['TIR'][0]
    
    # Compute the LST
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
