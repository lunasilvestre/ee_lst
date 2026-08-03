"""compute_emissivity.add_emissivity_band"""

import pytest

from ee_lst import compute_emissivity
from tests.conftest import expressions, numeric_args, renamed_bands, selected_bands

ASTER_GED = "NASA/ASTER_GED/AG100_003"

# Convolution coefficients that map ASTER bands 13/14 onto each Landsat
# thermal band, from Ermida et al. (2020). L9 is absent from the table and
# falls back to the L8 row.
CONVOLUTION = {
    "L4": (0.3222, 0.6498, 0.0272),
    "L5": (-0.0723, 1.0521, 0.0195),
    "L7": (0.2147, 0.7789, 0.0059),
    "L8": (0.6820, 0.2578, 0.0584),
}
L8_DEFAULT = CONVOLUTION["L8"]

WATER_BIT = 1 << 7  # 128
SNOW_BIT = 1 << 5  # 32


@pytest.fixture
def ee_mock(mocker):
    mocker.patch("ee_lst.aster_bare_emiss.ee")
    return mocker.patch("ee_lst.compute_emissivity.ee")


@pytest.mark.parametrize("sat,coeffs", CONVOLUTION.items())
def test_convolution_coefficients_per_satellite(image, ee_mock, sat, coeffs):
    compute_emissivity.add_emissivity_band(sat, True, image)
    wrapped = [c.args[0] for c in ee_mock.Image.call_args_list if c.args]
    for value in coeffs:
        assert value in wrapped, f"{sat}: coefficient {value} not used"


@pytest.mark.parametrize("sat", ["L9", "L3", "not-a-satellite"])
def test_unknown_satellite_falls_back_to_the_l8_row(image, ee_mock, sat):
    compute_emissivity.add_emissivity_band(sat, True, image)
    wrapped = [c.args[0] for c in ee_mock.Image.call_args_list if c.args]
    for value in L8_DEFAULT:
        assert value in wrapped


def test_convolution_formula_is_unmodified(image, ee_mock):
    compute_emissivity.add_emissivity_band("L8", True, image)
    formulas = [f for f, _ in expressions(image)]
    assert "c13 * EM13 + c14 * EM14 + c" in formulas


def test_dynamic_emissivity_mixes_bare_ground_with_vegetation(image, ee_mock):
    compute_emissivity.add_emissivity_band("L8", True, image)
    formulas = [f for f, _ in expressions(image)]
    assert "fvc * 0.99 + (1 - fvc) * em_bare" in formulas
    assert "FVC" in selected_bands(image)


def test_use_ndvi_true_selects_the_dynamic_branch(image, ee_mock):
    compute_emissivity.add_emissivity_band("L8", True, image)
    # The dynamic branch is the one that reads FVC.
    assert "FVC" in selected_bands(image)
    dynamic_expr = [f for f, _ in expressions(image) if f and "fvc" in f]
    assert dynamic_expr


def test_use_ndvi_false_reads_aster_directly(image, ee_mock):
    compute_emissivity.add_emissivity_band("L8", False, image)
    ee_mock.Image.assert_any_call(ASTER_GED)
    picked = selected_bands(ee_mock)
    assert "emissivity_band13" in picked
    assert "emissivity_band14" in picked


@pytest.mark.parametrize("use_ndvi", [True, False])
def test_aster_scale_factor_applied(image, ee_mock, use_ndvi):
    compute_emissivity.add_emissivity_band("L8", use_ndvi, image)
    multipliers = numeric_args(ee_mock, "multiply")
    assert 0.001 in multipliers


@pytest.mark.parametrize("use_ndvi", [True, False])
def test_water_and_snow_emissivity_are_prescribed(image, ee_mock, use_ndvi):
    compute_emissivity.add_emissivity_band("L8", use_ndvi, image)
    assert "QA_PIXEL" in selected_bands(image)
    bits = numeric_args(image, "bitwiseAnd")
    assert WATER_BIT in bits, "water bit not tested"
    assert SNOW_BIT in bits, "snow/ice bit not tested"
    replacements = numeric_args(image, "where")
    assert 0.99 in replacements, "water emissivity"
    assert 0.989 in replacements, "snow/ice emissivity"


@pytest.mark.parametrize("use_ndvi", [True, False])
def test_output_band_is_named_em(image, ee_mock, use_ndvi):
    compute_emissivity.add_emissivity_band("L8", use_ndvi, image)
    assert "EM" in renamed_bands(image)


def test_em_band_is_added_to_the_input_image(image, ee_mock):
    result = compute_emissivity.add_emissivity_band("L8", True, image)
    image.addBands.assert_called_once()
    assert result is image.addBands.return_value
