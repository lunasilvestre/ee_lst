"""aster_bare_emiss - bare-ground emissivity from the ASTER GED product."""

import pytest

from ee_lst import aster_bare_emiss
from tests.conftest import expressions, selected_bands

ASTER_GED = "NASA/ASTER_GED/AG100_003"

BAND_FUNCS = {
    "emissivity_band10": aster_bare_emiss.emiss_bare_band10,
    "emissivity_band11": aster_bare_emiss.emiss_bare_band11,
    "emissivity_band12": aster_bare_emiss.emiss_bare_band12,
    "emissivity_band13": aster_bare_emiss.emiss_bare_band13,
    "emissivity_band14": aster_bare_emiss.emiss_bare_band14,
}


@pytest.fixture
def ee_mock(mocker):
    return mocker.patch("ee_lst.aster_bare_emiss.ee")


def test_get_aster_image_loads_the_ged_product(ee_mock):
    aster_bare_emiss.get_aster_image()
    ee_mock.Image.assert_called_once_with(ASTER_GED)


def test_aster_fvc_rescales_the_stored_ndvi(ee_mock):
    # ASTER GED stores NDVI scaled by 100.
    aster_bare_emiss.get_aster_fvc()
    assert "ndvi" in selected_bands(ee_mock)
    ee_mock.Image.return_value.select.return_value.multiply.assert_any_call(0.01)


def test_aster_fvc_uses_the_same_endpoints_as_compute_fvc(ee_mock):
    aster_bare_emiss.get_aster_fvc()
    formula, bindings = expressions(ee_mock)[0]
    assert formula == "((ndvi - ndvi_bg) / (ndvi_vg - ndvi_bg)) ** 2"
    assert bindings["ndvi_bg"] == 0.2
    assert bindings["ndvi_vg"] == 0.86


def test_aster_fvc_is_clamped_to_the_unit_interval(ee_mock):
    aster_bare_emiss.get_aster_fvc()
    fvc = ee_mock.Image.return_value.select.return_value.multiply.return_value
    fvc.expression.return_value.lt.assert_any_call(0.0)
    fvc.expression.return_value.where.return_value.gt.assert_any_call(1.0)


@pytest.mark.parametrize("band", BAND_FUNCS)
def test_emiss_bare_band_selects_the_requested_band(image, ee_mock, band):
    aster_bare_emiss.emiss_bare_band(band, image)
    assert band in selected_bands(ee_mock)


def test_emiss_bare_band_rescales_stored_emissivity(image, ee_mock):
    # ASTER GED stores emissivity scaled by 1000.
    aster_bare_emiss.emiss_bare_band("emissivity_band13", image)
    ee_mock.Image.return_value.select.return_value.multiply.assert_any_call(0.001)


def test_emiss_bare_band_removes_the_vegetated_fraction(image, ee_mock):
    aster_bare_emiss.emiss_bare_band("emissivity_band13", image)
    formula, bindings = expressions(image)[0]
    # 0.99 is the emissivity assigned to full vegetation cover.
    assert formula == "(EM - 0.99 * fvc) / (1.0 - fvc)"
    assert set(bindings) == {"EM", "fvc"}


def test_emiss_bare_band_clips_to_the_image_geometry(image, ee_mock):
    aster_bare_emiss.emiss_bare_band("emissivity_band13", image)
    image.geometry.assert_called_once()
    image.expression.return_value.clip.assert_called_once_with(
        image.geometry.return_value
    )


@pytest.mark.parametrize("band,func", BAND_FUNCS.items())
def test_per_band_helpers_delegate_with_the_right_band(image, ee_mock, band, func):
    # The five helpers are near-identical one-liners; a copy-paste slip here
    # would silently compute band 13's emissivity under band 14's name.
    func(image)
    assert band in selected_bands(ee_mock)


def test_each_helper_targets_a_distinct_band(image, ee_mock):
    from unittest.mock import MagicMock

    seen = []
    for func in BAND_FUNCS.values():
        ee_mock.reset_mock()
        func(MagicMock())
        picked = [b for b in selected_bands(ee_mock) if b.startswith("emissivity_")]
        seen.append(picked[0])
    assert seen == list(BAND_FUNCS)
    assert len(set(seen)) == 5
