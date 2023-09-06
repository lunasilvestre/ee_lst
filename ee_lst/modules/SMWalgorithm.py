import ee
from python_modules import SMW_coefficients

def get_lookup_table(fc, prop_1, prop_2):
    """
    Create a lookup between two columns in a feature collection.
    """
    reducer = ee.Reducer.toList().repeat(2)
    lookup = fc.reduceColumns(reducer, [prop_1, prop_2])
    return ee.List(lookup.get('list'))

def add_band(landsat, image):
    """
    Apply the Stastical Mono-Window algorithm to compute the LST.

    Parameters:
    - landsat (str): ID of the Landsat satellite (e.g., 'L8')
    - image (ee.Image): Input Landsat image

    Returns:
    - ee.Image: Image with added LST band
    """
    
    # Select algorithm coefficients
    coeff_SMW = {
        'L4': SMW_coefficients.coeff_SMW_L4,
        'L5': SMW_coefficients.coeff_SMW_L5,
        'L7': SMW_coefficients.coeff_SMW_L7,
        'L8': SMW_coefficients.coeff_SMW_L8,
        'L9': SMW_coefficients.coeff_SMW_L9
    }.get(landsat, SMW_coefficients.coeff_SMW_L9)  # Default to L9 if not found
    
    # Create lookups for the algorithm coefficients
    A_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'A')
    B_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'B')
    C_lookup = get_lookup_table(coeff_SMW, 'TPWpos', 'C')
  
    # Map coefficients to the image using the TPW bin position
    A_img = image.remap(A_lookup.get(0), A_lookup.get(1), 0.0, 'TPWpos').resample('bilinear')
    B_img = image.remap(B_lookup.get(0), B_lookup.get(1), 0.0, 'TPWpos').resample('bilinear')
    C_img = image.remap(C_lookup.get(0), C_lookup.get(1), 0.0, 'TPWpos').resample('bilinear')
    
    # Select TIR band
    tir = {
        'L9': 'B10',
        'L8': 'B10',
        'L7': 'B6_VCID_1',
        'L4': 'B6',
        'L5': 'B6'
    }.get(landsat, 'B10')  # Default to B10 if not found
    
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

# You can add more functions as needed based on the content of the original `SMWalgorithm.js`.
