"""cloudmask.mask_sr / cloudmask.mask_toa

QA_PIXEL is a bitmask. Bit 3 is cloud, bit 4 is cloud shadow. The two functions
differ in exactly one respect: the surface-reflectance mask drops shadow too,
the top-of-atmosphere mask does not. That difference is the thing worth pinning.
"""

from ee_lst.cloudmask import mask_sr, mask_toa
from tests.conftest import numeric_args, selected_bands

CLOUD_BIT = 1 << 3  # 8
SHADOW_BIT = 1 << 4  # 16


def test_mask_sr_reads_qa_pixel(image):
    mask_sr(image)
    assert selected_bands(image) == ["QA_PIXEL", "QA_PIXEL"]


def test_mask_sr_masks_both_cloud_and_shadow(image):
    mask_sr(image)
    bits = numeric_args(image, "bitwiseAnd")
    assert CLOUD_BIT in bits
    assert SHADOW_BIT in bits


def test_mask_sr_keeps_pixels_where_neither_bit_is_set(image):
    mask_sr(image)
    assert 0 in numeric_args(image, "eq")
    image.updateMask.assert_called_once()


def test_mask_sr_returns_the_masked_image(image):
    assert mask_sr(image) is image.updateMask.return_value


def test_mask_toa_reads_qa_pixel(image):
    mask_toa(image)
    assert selected_bands(image) == ["QA_PIXEL"]


def test_mask_toa_masks_cloud_only(image):
    mask_toa(image)
    bits = numeric_args(image, "bitwiseAnd")
    assert bits == [CLOUD_BIT]
    # The distinguishing property: TOA does not drop cloud shadow.
    assert SHADOW_BIT not in bits


def test_mask_toa_keeps_pixels_where_the_cloud_bit_is_clear(image):
    mask_toa(image)
    assert 0 in numeric_args(image, "eq")
    image.updateMask.assert_called_once()


def test_mask_toa_returns_the_masked_image(image):
    assert mask_toa(image) is image.updateMask.return_value


def test_the_two_masks_differ_only_in_the_shadow_bit(image):
    from unittest.mock import MagicMock

    sr_image, toa_image = MagicMock(), MagicMock()
    mask_sr(sr_image)
    mask_toa(toa_image)
    sr_bits = set(numeric_args(sr_image, "bitwiseAnd"))
    toa_bits = set(numeric_args(toa_image, "bitwiseAnd"))
    assert sr_bits - toa_bits == {SHADOW_BIT}
