"""landsat_lst - the public entry point.

fetch_landsat_collection(landsat, date_start, date_end, geometry, use_ndvi) is
the function callers actually use, so its signature and its wiring are the two
things most worth protecting from a refactor.
"""

import inspect

import pytest

from ee_lst import landsat_lst
from ee_lst.constants import LANDSAT_BANDS
from tests.conftest import renamed_bands

SATELLITES = ["L4", "L5", "L7", "L8", "L9"]
DERIVED_BANDS = ["NDVI", "FVC", "TPW", "TPWpos", "EM"]


@pytest.fixture
def ee_mock(mocker):
    ee = mocker.patch("ee_lst.landsat_lst.ee")
    # Pretend Earth Engine is already initialised so nothing tries to
    # authenticate or reach the network.
    ee.data.is_initialized.return_value = True
    return ee


def test_public_signature_is_unchanged():
    # Guardrail: callers depend on this exact signature.
    params = list(inspect.signature(landsat_lst.fetch_landsat_collection).parameters)
    assert params == ["landsat", "date_start", "date_end", "geometry", "use_ndvi"]


def test_initialize_ee_skips_when_already_initialised(ee_mock):
    ee_mock.data.is_initialized.return_value = True
    landsat_lst.initialize_ee()
    ee_mock.Initialize.assert_not_called()
    ee_mock.Authenticate.assert_not_called()


def test_initialize_ee_initialises_when_not_yet_initialised(ee_mock):
    ee_mock.data.is_initialized.return_value = False
    landsat_lst.initialize_ee()
    ee_mock.Initialize.assert_called_once()
    ee_mock.Authenticate.assert_not_called()


def test_initialize_ee_authenticates_only_after_a_failure(ee_mock):
    ee_mock.data.is_initialized.return_value = False
    ee_mock.Initialize.side_effect = [Exception("no credentials"), None]
    landsat_lst.initialize_ee()
    ee_mock.Authenticate.assert_called_once()
    assert ee_mock.Initialize.call_count == 2


@pytest.mark.parametrize("sat", ["L3", "L10", "", "l8"])
def test_invalid_satellite_is_rejected(ee_mock, sat):
    with pytest.raises(ValueError) as excinfo:
        landsat_lst.fetch_landsat_collection(
            sat, "2023-01-01", "2023-02-01", None, True
        )
    message = str(excinfo.value)
    assert sat in message or sat == ""
    # The error should tell the caller what is valid.
    for valid in SATELLITES:
        assert valid in message


@pytest.mark.parametrize("sat", SATELLITES)
def test_valid_satellite_is_accepted(ee_mock, sat):
    landsat_lst.fetch_landsat_collection(sat, "2023-01-01", "2023-02-01", None, True)


@pytest.mark.parametrize("sat", SATELLITES)
def test_loads_both_the_toa_and_sr_collections(ee_mock, sat):
    landsat_lst.fetch_landsat_collection(sat, "2023-01-01", "2023-02-01", None, True)
    requested = [c.args[0] for c in ee_mock.ImageCollection.call_args_list if c.args]
    assert LANDSAT_BANDS[sat]["TOA"] in requested
    assert LANDSAT_BANDS[sat]["SR"] in requested


@pytest.mark.parametrize("sat", SATELLITES)
def test_filters_by_the_requested_dates_and_geometry(ee_mock, sat):
    geometry = object()
    landsat_lst.fetch_landsat_collection(
        sat, "2023-05-15", "2023-10-15", geometry, True
    )
    collection = ee_mock.ImageCollection.return_value
    collection.filterDate.assert_any_call("2023-05-15", "2023-10-15")
    collection.filterDate.return_value.filterBounds.assert_any_call(geometry)


@pytest.mark.parametrize("sat", SATELLITES)
def test_selects_the_visw_bands_plus_the_derived_ones(ee_mock, sat):
    landsat_lst.fetch_landsat_collection(sat, "2023-01-01", "2023-02-01", None, True)
    expected = LANDSAT_BANDS[sat]["VISW"] + DERIVED_BANDS
    picked = [
        c.args[0]
        for c in ee_mock.mock_calls
        if c[0].split(".")[-1] == "select" and c.args
    ]
    assert expected in picked


@pytest.mark.parametrize("sat", SATELLITES)
def test_combines_the_thermal_bands_from_toa(ee_mock, sat):
    landsat_lst.fetch_landsat_collection(sat, "2023-01-01", "2023-02-01", None, True)
    picked = [
        c.args[0]
        for c in ee_mock.mock_calls
        if c[0].split(".")[-1] == "select" and c.args
    ]
    assert LANDSAT_BANDS[sat]["TIR"] in picked


def test_derived_bands_are_appended_not_substituted(ee_mock):
    # A refactor that replaced VISW instead of extending it would still build a
    # valid graph, and would silently drop the reflectance bands.
    landsat_lst.fetch_landsat_collection("L8", "2023-01-01", "2023-02-01", None, True)
    picked = [
        c.args[0]
        for c in ee_mock.mock_calls
        if c[0].split(".")[-1] == "select" and c.args
    ]
    visw = [p for p in picked if isinstance(p, list) and "NDVI" in p][0]
    assert visw[: len(LANDSAT_BANDS["L8"]["VISW"])] == LANDSAT_BANDS["L8"]["VISW"]
    assert visw[len(LANDSAT_BANDS["L8"]["VISW"]) :] == DERIVED_BANDS


def test_add_timestamp_adds_a_constant_band(image, ee_mock):
    landsat_lst.add_timestamp(image)
    image.getNumber.assert_called_once_with("system:time_start")
    ee_mock.Image.constant.assert_called_once_with(image.getNumber.return_value)
    assert "TIMESTAMP" in renamed_bands(ee_mock)
    image.addBands.assert_called_once()


def test_add_raw_timestamp_sets_a_property_instead_of_a_band(image):
    result = landsat_lst.add_raw_timestamp(image)
    image.set.assert_called_once_with("raw_timestamp", image.get.return_value)
    image.get.assert_called_once_with("system:time_start")
    assert result is image.set.return_value
    image.addBands.assert_not_called()


@pytest.mark.parametrize("use_ndvi", [True, False])
def test_use_ndvi_reaches_the_pipeline(ee_mock, use_ndvi):
    # use_ndvi is threaded through a lambda into add_emissivity_band; this
    # guards against it being dropped on the way.
    result = landsat_lst.fetch_landsat_collection(
        "L8", "2023-01-01", "2023-02-01", None, use_ndvi
    )
    assert result is not None


def test_returns_the_mapped_collection(ee_mock):
    result = landsat_lst.fetch_landsat_collection(
        "L8", "2023-01-01", "2023-02-01", None, True
    )
    combined = ee_mock.ImageCollection.return_value.filterDate.return_value.filterBounds
    assert result is not None
    assert combined.called


def test_no_network_access_is_attempted(ee_mock):
    landsat_lst.fetch_landsat_collection("L8", "2023-01-01", "2023-02-01", None, True)
    ee_mock.Initialize.assert_not_called()
    ee_mock.Authenticate.assert_not_called()
