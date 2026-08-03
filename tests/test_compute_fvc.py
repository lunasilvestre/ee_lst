"""compute_fvc.add_fvc_band"""

import pytest

from ee_lst.compute_fvc import add_fvc_band
from tests.conftest import expressions, numeric_args, renamed_bands, selected_bands


def test_reads_the_ndvi_band(image):
    add_fvc_band("L8", image)
    assert "NDVI" in selected_bands(image)


def test_uses_the_published_ndvi_endpoints(image):
    add_fvc_band("L8", image)
    formula, bindings = expressions(image)[0]
    assert formula == "((ndvi - ndvi_bg) / (ndvi_vg - ndvi_bg)) ** 2"
    # Bare-soil and full-vegetation NDVI from Ermida et al. (2020).
    assert bindings["ndvi_bg"] == 0.2
    assert bindings["ndvi_vg"] == 0.86


def test_clamps_fvc_into_the_unit_interval(image):
    add_fvc_band("L8", image)
    fvc = image.expression.return_value
    # below 0 -> 0
    fvc.lt.assert_any_call(0.0)
    # above 1 -> 1
    fvc.where.return_value.gt.assert_any_call(1.0)
    replacements = numeric_args(image, "where")
    assert 0.0 in replacements and 1.0 in replacements


def test_output_band_is_named_fvc(image):
    add_fvc_band("L8", image)
    assert "FVC" in renamed_bands(image)


def test_fvc_band_is_added_to_the_input_image(image):
    result = add_fvc_band("L8", image)
    image.addBands.assert_called_once()
    assert result is image.addBands.return_value


@pytest.mark.parametrize("sat", ["L4", "L5", "L7", "L8", "L9"])
def test_satellite_argument_does_not_change_behaviour(image, sat):
    # add_fvc_band takes `landsat` only for signature consistency with its
    # siblings; FVC is derived from the NDVI band alone. If that ever stops
    # being true this test should be the thing that notices.
    add_fvc_band(sat, image)
    formula, bindings = expressions(image)[0]
    assert bindings["ndvi_bg"] == 0.2
    assert bindings["ndvi_vg"] == 0.86
    assert selected_bands(image) == ["NDVI"]
