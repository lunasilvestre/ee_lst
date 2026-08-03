"""ncep_tpw.add_tpw_band

Total precipitable water is interpolated from the NCEP reanalysis and then
binned into the 10 buckets the SMW coefficient table is indexed by, so the bin
edges here must line up with SMW_COEFFICIENTS.
"""

import pytest

from ee_lst import ncep_tpw
from ee_lst.constants import SMW_COEFFICIENTS
from tests.conftest import expressions, renamed_bands

NCEP_COLLECTION = "NCEP_RE/surface_wv"
SIX_HOURS_MS = 21600000


@pytest.fixture
def ee_mock(mocker):
    return mocker.patch("ee_lst.ncep_tpw.ee")


def test_reads_the_ncep_reanalysis_collection(image, ee_mock):
    ncep_tpw.add_tpw_band(image)
    ee_mock.ImageCollection.assert_called_once_with(NCEP_COLLECTION)


def test_uses_the_image_acquisition_time(image, ee_mock):
    ncep_tpw.add_tpw_band(image)
    image.get.assert_any_call("system:time_start")


def test_weights_by_distance_to_the_six_hourly_reanalysis_steps(image, ee_mock):
    # NCEP surface_wv is published every 6 hours; the interpolation weight is
    # the time offset expressed in those units.
    ncep_tpw.add_tpw_band(image)
    divisors = [
        a
        for name, args, _ in ee_mock.mock_calls
        if name.split(".")[-1] == "divide"
        for a in args
        if isinstance(a, (int, float))
    ]
    assert SIX_HOURS_MS in divisors


def test_adds_both_tpw_and_tpwpos_bands(image, ee_mock):
    ncep_tpw.add_tpw_band(image)
    names = renamed_bands(image, ee_mock)
    assert "TPW" in names
    assert "TPWpos" in names
    assert image.addBands.call_count >= 1


def test_bins_tpw_into_six_millimetre_buckets(image, ee_mock):
    ncep_tpw.add_tpw_band(image)
    formulas = [f for f, _ in expressions(ee_mock) if f and "TPW>" in f]
    assert formulas, "no TPW binning expression found"
    binning = formulas[0]
    # Buckets are 6mm wide from 0 to 54, then everything above 54 lands in 9.
    for upper in range(6, 55, 6):
        assert f"TPW<={upper}" in binning.replace(" ", "")
    assert "(TPW>54)?9" in binning.replace(" ", "")


def test_bin_count_matches_the_smw_coefficient_table(image, ee_mock):
    # TPWpos indexes SMW_COEFFICIENTS, so an 11th bucket here would read past
    # the end of every coefficient list.
    ncep_tpw.add_tpw_band(image)
    binning = [f for f, _ in expressions(ee_mock) if f and "TPW>" in f][0]
    # "...(TPW>0 && TPW<=6) ? 0: (TPW>6 && TPW<=12) ? 1: ..." - the value each
    # branch yields is the token right after a '?'.
    branches = binning.replace(" ", "").split("?")[1:]
    bins = sorted({int(b.split(":")[0]) for b in branches})
    assert bins == list(range(10))
    assert len(bins) == len(SMW_COEFFICIENTS["L8"])


def test_result_is_clipped_to_the_image_geometry(image, ee_mock):
    ncep_tpw.add_tpw_band(image)
    image.geometry.assert_called()
