"""smw_algorithm - the Statistical Mono-Window retrieval itself."""

import pytest

from ee_lst import smw_algorithm
from ee_lst.constants import LANDSAT_BANDS, SMW_COEFFICIENTS
from tests.conftest import expressions, renamed_bands, selected_bands

SATELLITES = ["L4", "L5", "L7", "L8", "L9"]


def test_lookup_table_returns_two_parallel_lists():
    coeff = [
        {"TPWpos": 0, "A": 1.0, "B": -2.0, "C": 3.0},
        {"TPWpos": 1, "A": 4.0, "B": -5.0, "C": 6.0},
    ]
    keys, values = smw_algorithm.get_lookup_table(coeff, "TPWpos", "A")
    assert keys == [0, 1]
    assert values == [1.0, 4.0]


def test_lookup_table_preserves_order():
    coeff = [{"k": i, "v": i * 10} for i in (3, 1, 2)]
    keys, values = smw_algorithm.get_lookup_table(coeff, "k", "v")
    assert keys == [3, 1, 2]
    assert values == [30, 10, 20]


@pytest.mark.parametrize("sat", SATELLITES)
def test_lookup_table_spans_every_tpw_bin(sat):
    keys, values = smw_algorithm.get_lookup_table(SMW_COEFFICIENTS[sat], "TPWpos", "A")
    assert keys == list(range(10))
    assert len(values) == 10


@pytest.mark.parametrize("sat", SATELLITES)
def test_remaps_coefficients_against_the_tpw_bin(image, sat):
    smw_algorithm.add_lst_band(sat, image)
    assert image.remap.call_count == 3, "expected one remap each for A, B and C"
    for call in image.remap.call_args_list:
        keys, values, default, band = call.args
        assert keys == list(range(10))
        assert len(values) == 10
        assert default == 0.0
        assert band == "TPWpos"


@pytest.mark.parametrize("sat", SATELLITES)
def test_remapped_values_come_from_that_satellites_table(image, sat):
    smw_algorithm.add_lst_band(sat, image)
    expected = {
        col: [row[col] for row in SMW_COEFFICIENTS[sat]] for col in ("A", "B", "C")
    }
    used = [call.args[1] for call in image.remap.call_args_list]
    assert used == [expected["A"], expected["B"], expected["C"]]


def test_l9_is_the_documented_coefficient_fallback():
    # The intent of `SMW_COEFFICIENTS.get(landsat, SMW_COEFFICIENTS["L9"])`.
    assert SMW_COEFFICIENTS.get("not-a-satellite", SMW_COEFFICIENTS["L9"]) is (
        SMW_COEFFICIENTS["L9"]
    )


def test_unknown_satellite_raises_before_the_l9_fallback_can_apply(image):
    """The L9 coefficient fallback is unreachable.

    add_lst_band defaults to L9 coefficients when `landsat` is unknown, but a
    few lines later reads LANDSAT_BANDS[landsat]["TIR"][0] with a direct index,
    which raises KeyError first. So the fallback can never actually apply.

    Pinned as current behaviour rather than fixed: changing it would alter
    behaviour, which this phase does not do. Note that fetch_landsat_collection
    validates `landsat` up front, so callers going through the public entry
    point never reach this path.
    """
    with pytest.raises(KeyError):
        smw_algorithm.add_lst_band("not-a-satellite", image)


@pytest.mark.parametrize("sat", SATELLITES)
def test_coefficients_are_resampled_bilinearly(image, sat):
    smw_algorithm.add_lst_band(sat, image)
    image.remap.return_value.resample.assert_called_with("bilinear")
    assert image.remap.return_value.resample.call_count == 3


@pytest.mark.parametrize("sat", SATELLITES)
def test_uses_the_first_thermal_band_of_the_satellite(image, sat):
    smw_algorithm.add_lst_band(sat, image)
    expected_tir = LANDSAT_BANDS[sat]["TIR"][0]
    assert expected_tir in selected_bands(image)


def test_landsat_7_uses_vcid_1_not_vcid_2(image):
    # L7 is the only satellite with two TIR bands; picking the second would be
    # a plausible off-by-one and would change every retrieved temperature.
    smw_algorithm.add_lst_band("L7", image)
    picked = selected_bands(image)
    assert "B6_VCID_1" in picked
    assert "B6_VCID_2" not in picked


@pytest.mark.parametrize("sat", SATELLITES)
def test_mono_window_formula_is_unmodified(image, sat):
    smw_algorithm.add_lst_band(sat, image)
    formula, bindings = expressions(image)[0]
    assert formula == "A * Tb1 / em1 + B / em1 + C"
    assert set(bindings) == {"A", "B", "C", "em1", "Tb1"}


@pytest.mark.parametrize("sat", SATELLITES)
def test_reads_the_emissivity_band(image, sat):
    smw_algorithm.add_lst_band(sat, image)
    assert "EM" in selected_bands(image)


def test_masks_pixels_with_negative_precipitable_water(image):
    smw_algorithm.add_lst_band("L8", image)
    assert "TPW" in selected_bands(image)
    image.select.return_value.lt.assert_any_call(0)
    image.select.return_value.lt.return_value.Not.assert_called()
    image.expression.return_value.updateMask.assert_called_once()


@pytest.mark.parametrize("sat", SATELLITES)
def test_output_band_is_named_lst(image, sat):
    smw_algorithm.add_lst_band(sat, image)
    assert "LST" in renamed_bands(image)


def test_lst_band_is_added_to_the_input_image(image):
    result = smw_algorithm.add_lst_band("L8", image)
    image.addBands.assert_called_once()
    assert result is image.addBands.return_value
