"""compute_ndvi.add_ndvi_band"""

import pytest

from ee_lst.compute_ndvi import add_ndvi_band
from tests.conftest import expressions, renamed_bands, selected_bands

# Landsat 8/9 shifted the band numbering: NIR moved from SR_B4 to SR_B5.
# Getting this branch wrong is silent - the graph still builds, the numbers are
# just wrong - so it is the single most valuable thing in this file.
NIR_RED = {
    "L4": ("SR_B4", "SR_B3"),
    "L5": ("SR_B4", "SR_B3"),
    "L7": ("SR_B4", "SR_B3"),
    "L8": ("SR_B5", "SR_B4"),
    "L9": ("SR_B5", "SR_B4"),
}


@pytest.mark.parametrize("sat,expected", NIR_RED.items())
def test_selects_the_right_nir_and_red_bands(image, sat, expected):
    add_ndvi_band(sat, image)
    # The bindings dict is built nir-first, so call order pins which is which.
    assert selected_bands(image)[:2] == list(expected)


def test_unknown_satellite_falls_back_to_legacy_band_numbering(image):
    add_ndvi_band("L3", image)
    assert selected_bands(image)[:2] == ["SR_B4", "SR_B3"]


@pytest.mark.parametrize("sat", NIR_RED)
def test_applies_the_collection_2_scale_and_offset(image, sat):
    add_ndvi_band(sat, image)
    scaled = image.select.return_value.multiply
    scaled.assert_any_call(0.0000275)
    scaled.return_value.add.assert_any_call(-0.2)


@pytest.mark.parametrize("sat", NIR_RED)
def test_uses_the_normalised_difference_formula(image, sat):
    add_ndvi_band(sat, image)
    formula, bindings = expressions(image)[0]
    assert formula == "(nir - red) / (nir + red)"
    assert set(bindings) == {"nir", "red"}


@pytest.mark.parametrize("sat", NIR_RED)
def test_output_band_is_named_ndvi(image, sat):
    add_ndvi_band(sat, image)
    assert "NDVI" in renamed_bands(image)


def test_ndvi_band_is_added_to_the_input_image(image):
    result = add_ndvi_band("L8", image)
    renamed = image.expression.return_value.rename.return_value
    image.addBands.assert_called_once_with(renamed)
    assert result is image.addBands.return_value
