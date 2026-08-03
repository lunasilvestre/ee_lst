"""broadband_emiss.add_band - broad-band emissivity from the five ASTER bands."""

import re

import pytest

from ee_lst import broadband_emiss
from tests.conftest import expressions, renamed_bands, selected_bands

ASTER_GED = "NASA/ASTER_GED/AG100_003"

# Weights from Ermida et al. (2020), eq. for broad-band emissivity.
BBE_WEIGHTS = {
    "intercept": 0.128,
    "em10": 0.014,
    "em11": 0.145,
    "em12": 0.241,
    "em13": 0.467,
    "em14": 0.004,
}


@pytest.fixture
def ee_mock(mocker):
    mocker.patch("ee_lst.aster_bare_emiss.ee")
    return mocker.patch("ee_lst.broadband_emiss.ee")


def test_loads_the_aster_ged_product(image, ee_mock):
    broadband_emiss.add_band(True, image)
    ee_mock.Image.assert_any_call(ASTER_GED)


def test_uses_all_five_aster_emissivity_bands(image, ee_mock):
    broadband_emiss.add_band(True, image)
    picked = {b for b in selected_bands(ee_mock) if b.startswith("emissivity_band")}
    assert picked == {f"emissivity_band{n}" for n in range(10, 15)}


def test_broadband_weights_are_unmodified(image, ee_mock):
    broadband_emiss.add_band(True, image)
    formula = [f for f, _ in expressions(image) if f and "em10" in f][0]
    numbers = [float(n) for n in re.findall(r"\d+\.\d+", formula)]
    assert numbers == [
        BBE_WEIGHTS["intercept"],
        BBE_WEIGHTS["em10"],
        BBE_WEIGHTS["em11"],
        BBE_WEIGHTS["em12"],
        BBE_WEIGHTS["em13"],
        BBE_WEIGHTS["em14"],
    ]


def test_broadband_expression_binds_all_five_bands(image, ee_mock):
    broadband_emiss.add_band(True, image)
    _, bindings = [(f, b) for f, b in expressions(image) if f and "em10" in f][0]
    assert set(bindings) == {"em10", "em11", "em12", "em13", "em14"}


def test_weights_sum_to_approximately_one_with_the_intercept():
    # A transcription slip in any single weight shows up here.
    total = BBE_WEIGHTS["intercept"] + sum(
        v for k, v in BBE_WEIGHTS.items() if k != "intercept"
    )
    assert total == pytest.approx(0.999, abs=0.002)


@pytest.mark.parametrize("dynamic", [True, False])
def test_dynamic_flag_is_handed_to_earth_engine_not_python(image, ee_mock, dynamic):
    # The choice is deferred to the server via ee.Algorithms.If, so both
    # branches are always built - a Python-side `if` here would be a bug.
    broadband_emiss.add_band(dynamic, image)
    assert ee_mock.Algorithms.If.call_count == 5
    for call in ee_mock.Algorithms.If.call_args_list:
        assert call.args[0] is dynamic


@pytest.mark.parametrize("dynamic", [True, False])
def test_vegetation_correction_uses_the_fvc_band(image, ee_mock, dynamic):
    broadband_emiss.add_band(dynamic, image)
    assert "FVC" in selected_bands(image)
    dynam = [
        f for f, _ in expressions(image) if f == "fvc * 0.99 + (1 - fvc) * em_bare"
    ]
    assert len(dynam) == 5


def test_rescales_stored_aster_emissivity(image, ee_mock):
    # ASTER GED stores emissivity scaled by 1000.
    broadband_emiss.add_band(False, image)
    aster = ee_mock.Image.return_value.clip.return_value
    aster.select.return_value.multiply.assert_any_call(0.001)


@pytest.mark.parametrize("dynamic", [True, False])
def test_output_band_is_named_bbe(image, ee_mock, dynamic):
    broadband_emiss.add_band(dynamic, image)
    assert "BBE" in renamed_bands(image)


def test_bbe_band_is_added_to_the_input_image(image, ee_mock):
    result = broadband_emiss.add_band(True, image)
    image.addBands.assert_called_once()
    assert result is image.addBands.return_value
