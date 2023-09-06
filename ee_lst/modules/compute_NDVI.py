import ee

def add_band(landsat, image):
    """
    Compute NDVI values for a given Landsat image.

    Parameters:
    - landsat (str): ID of the Landsat satellite (e.g., 'L8')
    - image (ee.Image): Input Landsat image

    Returns:
    - ee.Image: Image with added NDVI band
    """
    
    # Choose bands based on the Landsat satellite ID
    if landsat in ['L8', 'L9']:
        nir = 'SR_B5'
        red = 'SR_B4'
    else:
        nir = 'SR_B4'
        red = 'SR_B3'
    
    # Compute NDVI
    ndvi = image.expression(
        '(nir - red) / (nir + red)',
        {
            'nir': image.select(nir).multiply(0.0000275).add(-0.2),
            'red': image.select(red).multiply(0.0000275).add(-0.2)
        }
    ).rename('NDVI')
    
    return image.addBands(ndvi)

# You can add more functions as needed based on the content of the original `compute_NDVI.js`.
