"""The numbers this library exists to reproduce.

ee_lst's value is that it matches Ermida et al. (2020). If a coefficient moves,
the port is wrong even when every other test passes - so these are pinned to
literal values rather than derived from the module under test.
"""

import pytest

from ee_lst.constants import LANDSAT_BANDS, SMW_COEFFICIENTS

SATELLITES = ["L4", "L5", "L7", "L8", "L9"]

# Landsat 4/5/7 carry no SR_B6; 8/9 do.
VISW_LEGACY = ["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7", "QA_PIXEL"]
VISW_MODERN = [
    "SR_B1",
    "SR_B2",
    "SR_B3",
    "SR_B4",
    "SR_B5",
    "SR_B6",
    "SR_B7",
    "QA_PIXEL",
]

EXPECTED_BANDS = {
    "L4": {
        "TOA": "LANDSAT/LT04/C02/T1_TOA",
        "SR": "LANDSAT/LT04/C02/T1_L2",
        "TIR": ["B6"],
        "VISW": VISW_LEGACY,
    },
    "L5": {
        "TOA": "LANDSAT/LT05/C02/T1_TOA",
        "SR": "LANDSAT/LT05/C02/T1_L2",
        "TIR": ["B6"],
        "VISW": VISW_LEGACY,
    },
    "L7": {
        "TOA": "LANDSAT/LE07/C02/T1_TOA",
        "SR": "LANDSAT/LE07/C02/T1_L2",
        "TIR": ["B6_VCID_1", "B6_VCID_2"],
        "VISW": VISW_LEGACY,
    },
    "L8": {
        "TOA": "LANDSAT/LC08/C02/T1_TOA",
        "SR": "LANDSAT/LC08/C02/T1_L2",
        "TIR": ["B10", "B11"],
        "VISW": VISW_MODERN,
    },
    "L9": {
        "TOA": "LANDSAT/LC09/C02/T1_TOA",
        "SR": "LANDSAT/LC09/C02/T1_L2",
        "TIR": ["B10", "B11"],
        "VISW": VISW_MODERN,
    },
}


def test_landsat_bands_covers_exactly_the_supported_satellites():
    assert sorted(LANDSAT_BANDS) == SATELLITES


@pytest.mark.parametrize("sat", SATELLITES)
def test_landsat_bands_entry_is_complete_and_unmodified(sat):
    assert LANDSAT_BANDS[sat] == EXPECTED_BANDS[sat]


@pytest.mark.parametrize("sat", SATELLITES)
def test_every_satellite_declares_a_thermal_band(sat):
    assert LANDSAT_BANDS[sat]["TIR"], f"{sat} has no TIR band"


@pytest.mark.parametrize("sat", SATELLITES)
def test_qa_pixel_present_for_cloud_masking(sat):
    # cloudmask.mask_sr / mask_toa both select QA_PIXEL unconditionally.
    assert "QA_PIXEL" in LANDSAT_BANDS[sat]["VISW"]


def test_smw_coefficients_covers_exactly_the_supported_satellites():
    assert sorted(SMW_COEFFICIENTS) == SATELLITES


@pytest.mark.parametrize("sat", SATELLITES)
def test_smw_has_ten_contiguous_tpw_bins(sat):
    rows = SMW_COEFFICIENTS[sat]
    assert len(rows) == 10
    assert [r["TPWpos"] for r in rows] == list(range(10))


@pytest.mark.parametrize("sat", SATELLITES)
def test_smw_rows_have_exactly_the_expected_keys(sat):
    for row in SMW_COEFFICIENTS[sat]:
        assert set(row) == {"TPWpos", "A", "B", "C"}


# First and last bin of each satellite, pinned to the published values. A full
# 50-row table would be unreadable; the endpoints catch a shifted or truncated
# table, and test_smw_has_ten_contiguous_tpw_bins catches reordering.
SMW_ENDPOINTS = {
    "L4": ((0.9755, -205.2767, 212.0051), (2.0215, -571.8563, 279.9854)),
    "L5": ((0.9765, -204.6584, 211.1321), (2.1168, -600.7079, 282.4583)),
    "L7": ((0.9764, -205.3511, 211.8507), (2.0533, -581.2619, 280.6800)),
    "L8": ((0.9751, -205.8929, 212.7173), (1.9403, -547.2681, 277.9953)),
    "L9": ((0.9751, -206.2187, 213.0526), (1.9223, -541.7084, 277.4964)),
}


@pytest.mark.parametrize("sat", SATELLITES)
def test_smw_endpoint_coefficients_unmodified(sat):
    first, last = SMW_ENDPOINTS[sat]
    rows = SMW_COEFFICIENTS[sat]
    assert (rows[0]["A"], rows[0]["B"], rows[0]["C"]) == first
    assert (rows[-1]["A"], rows[-1]["B"], rows[-1]["C"]) == last


@pytest.mark.parametrize("sat", SATELLITES)
def test_smw_a_coefficient_follows_the_published_shape(sat):
    # In all five published tables A climbs steadily across bins 0-7, dips at
    # bin 8, then peaks at bin 9. Encoding that shape catches a transposed or
    # mis-transcribed row that endpoint checks alone would miss.
    a_values = [r["A"] for r in SMW_COEFFICIENTS[sat]]
    assert a_values[:8] == sorted(a_values[:8]), "bins 0-7 should be increasing"
    assert len(set(a_values[:8])) == 8, "bins 0-7 should be strictly increasing"
    assert a_values[8] < a_values[7], "bin 8 dips in every published table"
    assert a_values[9] == max(a_values), "bin 9 is the maximum"
    assert all(a > 0 for a in a_values)


@pytest.mark.parametrize("sat", SATELLITES)
def test_smw_b_negative_and_c_positive(sat):
    for row in SMW_COEFFICIENTS[sat]:
        assert row["B"] < 0, f"{sat} bin {row['TPWpos']}: B should be negative"
        assert row["C"] > 0, f"{sat} bin {row['TPWpos']}: C should be positive"


def test_both_tables_describe_the_same_satellites():
    assert sorted(LANDSAT_BANDS) == sorted(SMW_COEFFICIENTS)
