# import ee


def mask_sr(image):
    """
    Apply cloud mask to surface reflectance Landsat image.

    Parameters:
    - image (ee.Image): Input Landsat image.

    Returns:
    - ee.Image: Cloud-masked Landsat image.
    """

    cloud_mask = (
        image.select("QA_PIXEL")
        .bitwiseAnd(1 << 3)
        .Or(image.select("QA_PIXEL").bitwiseAnd(1 << 4))
        .eq(0)
    )
    return image.updateMask(cloud_mask)


def mask_toa(image):
    """
    Apply cloud mask to top-of-atmosphere reflectance Landsat image.

    Parameters:
    - image (ee.Image): Input Landsat image.

    Returns:
    - ee.Image: Cloud-masked Landsat image.
    """

    cloud_mask = image.select("QA_PIXEL").bitwiseAnd(1 << 3).eq(0)
    return image.updateMask(cloud_mask)
