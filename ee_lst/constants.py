# Landsat satellites TOA, SR, TIR and VISW bands
LANDSAT_BANDS = {
    'L4': {
        'TOA': 'LANDSAT/LT04/C02/T1_TOA',
        'SR': 'LANDSAT/LT04/C02/T1_L2',
        'TIR': ['B6'],
        'VISW': ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'QA_PIXEL']
    },
    'L5': {
        'TOA': 'LANDSAT/LT05/C02/T1_TOA',
        'SR': 'LANDSAT/LT05/C02/T1_L2',
        'TIR': ['B6',],
        'VISW': ['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B7','QA_PIXEL']
    },
    'L7': {
        'TOA': 'LANDSAT/LE07/C02/T1_TOA',
        'SR': 'LANDSAT/LE07/C02/T1_L2',
        'TIR': ['B6_VCID_1','B6_VCID_2'],
        'VISW': ['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B7','QA_PIXEL']
    },
    'L8': {
        'TOA': 'LANDSAT/LC08/C02/T1_TOA',
        'SR': 'LANDSAT/LC08/C02/T1_L2',
        'TIR': ['B10','B11'],
        'VISW': ['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7','QA_PIXEL']
    },
    'L9': {
        'TOA': 'LANDSAT/LC09/C02/T1_TOA',
        'SR': 'LANDSAT/LC09/C02/T1_L2',
        'TIR': ['B10','B11'],
        'VISW': ['SR_B1','SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7','QA_PIXEL']
    }
}