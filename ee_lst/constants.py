# Landsat satellites TOA, SR, TIR and VISW bands
LANDSAT_BANDS = {
    "L4": {
        "TOA": "LANDSAT/LT04/C02/T1_TOA",
        "SR": "LANDSAT/LT04/C02/T1_L2",
        "TIR": ["B6"],
        "VISW": ["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7", "QA_PIXEL"],
    },
    "L5": {
        "TOA": "LANDSAT/LT05/C02/T1_TOA",
        "SR": "LANDSAT/LT05/C02/T1_L2",
        "TIR": ["B6"],
        "VISW": ["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7", "QA_PIXEL"],
    },
    "L7": {
        "TOA": "LANDSAT/LE07/C02/T1_TOA",
        "SR": "LANDSAT/LE07/C02/T1_L2",
        "TIR": ["B6_VCID_1", "B6_VCID_2"],
        "VISW": ["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7", "QA_PIXEL"],
    },
    "L8": {
        "TOA": "LANDSAT/LC08/C02/T1_TOA",
        "SR": "LANDSAT/LC08/C02/T1_L2",
        "TIR": ["B10", "B11"],
        "VISW": [
            "SR_B1",
            "SR_B2",
            "SR_B3",
            "SR_B4",
            "SR_B5",
            "SR_B6",
            "SR_B7",
            "QA_PIXEL",
        ],
    },
    "L9": {
        "TOA": "LANDSAT/LC09/C02/T1_TOA",
        "SR": "LANDSAT/LC09/C02/T1_L2",
        "TIR": ["B10", "B11"],
        "VISW": [
            "SR_B1",
            "SR_B2",
            "SR_B3",
            "SR_B4",
            "SR_B5",
            "SR_B6",
            "SR_B7",
            "QA_PIXEL",
        ],
    },
}

# Coefficients for the Statistical Mono-Window Algorithm
SMW_COEFFICIENTS = {
    "L4": [
        {"TPWpos": 0, "A": 0.9755, "B": -205.2767, "C": 212.0051},
        {"TPWpos": 1, "A": 1.0155, "B": -233.8902, "C": 230.4049},
        {"TPWpos": 2, "A": 1.0672, "B": -257.1884, "C": 239.3072},
        {"TPWpos": 3, "A": 1.1499, "B": -286.2166, "C": 244.8497},
        {"TPWpos": 4, "A": 1.2277, "B": -316.7643, "C": 253.0033},
        {"TPWpos": 5, "A": 1.3649, "B": -361.8276, "C": 258.5471},
        {"TPWpos": 6, "A": 1.5085, "B": -410.1157, "C": 265.1131},
        {"TPWpos": 7, "A": 1.7045, "B": -472.4909, "C": 270.7000},
        {"TPWpos": 8, "A": 1.5886, "B": -442.9489, "C": 277.1511},
        {"TPWpos": 9, "A": 2.0215, "B": -571.8563, "C": 279.9854},
    ],
    "L5": [
        {"TPWpos": 0, "A": 0.9765, "B": -204.6584, "C": 211.1321},
        {"TPWpos": 1, "A": 1.0229, "B": -235.5384, "C": 230.0619},
        {"TPWpos": 2, "A": 1.0817, "B": -261.3886, "C": 239.5256},
        {"TPWpos": 3, "A": 1.1738, "B": -293.6128, "C": 245.6042},
        {"TPWpos": 4, "A": 1.2605, "B": -327.1417, "C": 254.2301},
        {"TPWpos": 5, "A": 1.4166, "B": -377.7741, "C": 259.9711},
        {"TPWpos": 6, "A": 1.5727, "B": -430.0388, "C": 266.9520},
        {"TPWpos": 7, "A": 1.7879, "B": -498.1947, "C": 272.8413},
        {"TPWpos": 8, "A": 1.6347, "B": -457.8183, "C": 279.6160},
        {"TPWpos": 9, "A": 2.1168, "B": -600.7079, "C": 282.4583},
    ],
    "L7": [
        {"TPWpos": 0, "A": 0.9764, "B": -205.3511, "C": 211.8507},
        {"TPWpos": 1, "A": 1.0201, "B": -235.2416, "C": 230.5468},
        {"TPWpos": 2, "A": 1.0750, "B": -259.6560, "C": 239.6619},
        {"TPWpos": 3, "A": 1.1612, "B": -289.8190, "C": 245.3286},
        {"TPWpos": 4, "A": 1.2425, "B": -321.4658, "C": 253.6144},
        {"TPWpos": 5, "A": 1.3864, "B": -368.4078, "C": 259.1390},
        {"TPWpos": 6, "A": 1.5336, "B": -417.7796, "C": 265.7486},
        {"TPWpos": 7, "A": 1.7345, "B": -481.5714, "C": 271.3659},
        {"TPWpos": 8, "A": 1.6066, "B": -448.5071, "C": 277.9058},
        {"TPWpos": 9, "A": 2.0533, "B": -581.2619, "C": 280.6800},
    ],
    "L8": [
        {"TPWpos": 0, "A": 0.9751, "B": -205.8929, "C": 212.7173},
        {"TPWpos": 1, "A": 1.0090, "B": -232.2750, "C": 230.5698},
        {"TPWpos": 2, "A": 1.0541, "B": -253.1943, "C": 238.9548},
        {"TPWpos": 3, "A": 1.1282, "B": -279.4212, "C": 244.0772},
        {"TPWpos": 4, "A": 1.1987, "B": -307.4497, "C": 251.8341},
        {"TPWpos": 5, "A": 1.3205, "B": -348.0228, "C": 257.2740},
        {"TPWpos": 6, "A": 1.4540, "B": -393.1718, "C": 263.5599},
        {"TPWpos": 7, "A": 1.6350, "B": -451.0790, "C": 268.9405},
        {"TPWpos": 8, "A": 1.5468, "B": -429.5095, "C": 275.0895},
        {"TPWpos": 9, "A": 1.9403, "B": -547.2681, "C": 277.9953},
    ],
    "L9": [
        {"TPWpos": 0, "A": 0.9751, "B": -206.2187, "C": 213.0526},
        {"TPWpos": 1, "A": 1.0093, "B": -232.7408, "C": 230.9401},
        {"TPWpos": 2, "A": 1.0539, "B": -253.4430, "C": 239.2572},
        {"TPWpos": 3, "A": 1.1267, "B": -279.1685, "C": 244.2379},
        {"TPWpos": 4, "A": 1.1961, "B": -306.7961, "C": 251.8873},
        {"TPWpos": 5, "A": 1.3155, "B": -346.5312, "C": 257.2174},
        {"TPWpos": 6, "A": 1.4463, "B": -390.7794, "C": 263.3479},
        {"TPWpos": 7, "A": 1.6229, "B": -447.2745, "C": 268.5970},
        {"TPWpos": 8, "A": 1.5396, "B": -427.0904, "C": 274.6380},
        {"TPWpos": 9, "A": 1.9223, "B": -541.7084, "C": 277.4964},
    ],
}