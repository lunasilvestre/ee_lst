import ee

def add_band(landsat, image):
    """
    Compute Fraction of Vegetation Cover (FVC) for a given Landsat image using NDVI.

    Parameters:
    - landsat (str): ID of the Landsat satellite (e.g., 'L8'). Currently not used but kept for consistency.
    - image (ee.Image): Input Landsat image with NDVI band

    Returns:
    - ee.Image: Image with added FVC band
    """
    
    ndvi = image.select('NDVI')
    
    # Compute FVC
    fvc = image.expression(
        '((ndvi - ndvi_bg) / (ndvi_vg - ndvi_bg)) ** 2',
        {
            'ndvi': ndvi,
            'ndvi_bg': 0.2,
            'ndvi_vg': 0.86
        }
    )
    
    # Apply constraints to FVC values
    fvc = fvc.where(fvc.lt(0.0), 0.0)
    fvc = fvc.where(fvc.gt(1.0), 1.0)
    
    return image.addBands(fvc.rename('FVC'))

# You can add more functions as needed based on the content of the original `compute_FVC.js`.
