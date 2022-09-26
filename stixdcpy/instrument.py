import math
import numpy as np


nominal_grid_parameters = {
    "1": {
        "Label": "3c",
        "SlitWidth": 0.0419,
        "FrontPitch": 0.078039,
        "FrontOrient": 169.9559,
        "RearPitch": 0.077364,
        "RearOrient": 170.0437,
        "PitchToler": 0.0000245,
        "OrientToler": 0.0181,
        "BridgePitch": 1.13,
        "BridgeOrient": 80,
        "BridgeWidth": 0.05
    },
    "2": {
        "Label": "5c",
        "SlitWidth": 0.0825,
        "FrontPitch": 0.158078,
        "FrontOrient": 130.3942,
        "RearPitch": 0.159925,
        "RearOrient": 129.6012,
        "PitchToler": 0.000103,
        "OrientToler": 0.037,
        "BridgePitch": 1.97,
        "BridgeOrient": 40,
        "BridgeWidth": 0.05
    },
    "3": {
        "Label": "10a",
        "SlitWidth": 0.4793,
        "FrontPitch": 0.909644,
        "FrontOrient": 151.4808,
        "RearPitch": 0.999045,
        "RearOrient": 148.3736,
        "PitchToler": 0.00368,
        "OrientToler": 0.222,
        "BridgePitch": "NA",
        "BridgeOrient": "NA",
        "BridgeWidth": "NA"
    },
    "4": {
        "Label": "8c",
        "SlitWidth": 0.2358,
        "FrontPitch": 0.461187,
        "FrontOrient": 68.589,
        "RearPitch": 0.469602,
        "RearOrient": 71.4367,
        "PitchToler": 0.000879,
        "OrientToler": 0.108,
        "BridgePitch": 3.15,
        "BridgeOrient": 160,
        "BridgeWidth": 0.05
    },
    "5": {
        "Label": "4b",
        "SlitWidth": 0.0586,
        "FrontPitch": 0.110594,
        "FrontOrient": 29.82,
        "RearPitch": 0.111811,
        "RearOrient": 30.182,
        "PitchToler": 0.0000502,
        "OrientToler": 0.0259,
        "BridgePitch": 1.69,
        "BridgeOrient": 120,
        "BridgeWidth": 0.05
    },
    "6": {
        "Label": "5a",
        "SlitWidth": 0.0825,
        "FrontPitch": 0.158505,
        "FrontOrient": 69.5151,
        "RearPitch": 0.159487,
        "RearOrient": 70.4879,
        "PitchToler": 0.000103,
        "OrientToler": 0.037,
        "BridgePitch": 1.58,
        "BridgeOrient": 160,
        "BridgeWidth": 0.05
    },
    "7": {
        "Label": "3a",
        "SlitWidth": 0.0419,
        "FrontPitch": 0.077582,
        "FrontOrient": 110.2373,
        "RearPitch": 0.077817,
        "RearOrient": 109.7619,
        "PitchToler": 0.0000245,
        "OrientToler": 0.0181,
        "BridgePitch": 1.05,
        "BridgeOrient": 20,
        "BridgeWidth": 0.05
    },
    "8": {
        "Label": "7b",
        "SlitWidth": 0.1657,
        "FrontPitch": 0.320259,
        "FrontOrient": 150.5213,
        "RearPitch": 0.33068,
        "RearOrient": 149.4617,
        "PitchToler": 0.00043,
        "OrientToler": 0.0757,
        "BridgePitch": 2.66,
        "BridgeOrient": 60,
        "BridgeWidth": 0.05
    },
    "9": {
        "Label": "CFL",
        "SlitWidth": "NA",
        "FrontPitch": "NA",
        "FrontOrient": "NA",
        "RearPitch": "NA",
        "RearOrient": "NA",
        "PitchToler": "NA",
        "OrientToler": "NA",
        "BridgePitch": "NA",
        "BridgeOrient": "NA",
        "BridgeWidth": "NA"
    },
    "10": {
        "Label": "BKG",
        "SlitWidth": "NA",
        "FrontPitch": "NA",
        "FrontOrient": "NA",
        "RearPitch": "NA",
        "RearOrient": "NA",
        "PitchToler": "NA",
        "OrientToler": "NA",
        "BridgePitch": "NA",
        "BridgeOrient": "NA",
        "BridgeWidth": "NA"
    },
    "11": {
        "Label": "1a",
        "SlitWidth": 0.022,
        "FrontPitch": 0.037929,
        "FrontOrient": 150.0617,
        "RearPitch": 0.038071,
        "RearOrient": 149.938,
        "PitchToler": 0.00000586,
        "OrientToler": 0.00884,
        "BridgePitch": 1.1,
        "BridgeOrient": 60,
        "BridgeWidth": 0.05
    },
    "12": {
        "Label": "2a",
        "SlitWidth": 0.0302,
        "FrontPitch": 0.054408,
        "FrontOrient": 129.8643,
        "RearPitch": 0.054192,
        "RearOrient": 130.1351,
        "PitchToler": 0.000012,
        "OrientToler": 0.0126,
        "BridgePitch": 1.18,
        "BridgeOrient": 40,
        "BridgeWidth": 0.05
    },
    "13": {
        "Label": "1b",
        "SlitWidth": 0.022,
        "FrontPitch": 0.038,
        "FrontOrient": 90.1237,
        "RearPitch": 0.038,
        "RearOrient": 89.8763,
        "PitchToler": 0.00000586,
        "OrientToler": 0.00884,
        "BridgePitch": 1.1,
        "BridgeOrient": 0,
        "BridgeWidth": 0.05
    },
    "14": {
        "Label": "9b",
        "SlitWidth": 0.336,
        "FrontPitch": 0.674193,
        "FrontOrient": 107.9371,
        "RearPitch": 0.656988,
        "RearOrient": 112.0102,
        "PitchToler": 0.0018,
        "OrientToler": 0.155,
        "BridgePitch": "NA",
        "BridgeOrient": "NA",
        "BridgeWidth": "NA"
    },
    "15": {
        "Label": "6a",
        "SlitWidth": 0.1168,
        "FrontPitch": 0.229395,
        "FrontOrient": 50.5721,
        "RearPitch": 0.225614,
        "RearOrient": 49.4374,
        "PitchToler": 0.00021,
        "OrientToler": 0.0529,
        "BridgePitch": 1.97,
        "BridgeOrient": 140,
        "BridgeWidth": 0.05
    },
    "16": {
        "Label": "9a",
        "SlitWidth": 0.336,
        "FrontPitch": 0.641967,
        "FrontOrient": 170.3629,
        "RearPitch": 0.691656,
        "RearOrient": 169.609,
        "PitchToler": 0.0018,
        "OrientToler": 0.155,
        "BridgePitch": "NA",
        "BridgeOrient": "NA",
        "BridgeWidth": "NA"
    },
    "17": {
        "Label": "2c",
        "SlitWidth": 0.0302,
        "FrontPitch": 0.054136,
        "FrontOrient": 9.9694,
        "RearPitch": 0.054465,
        "RearOrient": 10.0308,
        "PitchToler": 0.000012,
        "OrientToler": 0.0126,
        "BridgePitch": 1.13,
        "BridgeOrient": 100,
        "BridgeWidth": 0.05
    },
    "18": {
        "Label": "1c",
        "SlitWidth": 0.022,
        "FrontPitch": 0.037929,
        "FrontOrient": 29.9383,
        "RearPitch": 0.038071,
        "RearOrient": 30.062,
        "PitchToler": 0.00000586,
        "OrientToler": 0.00884,
        "BridgePitch": 1.1,
        "BridgeOrient": 120,
        "BridgeWidth": 0.05
    },
    "19": {
        "Label": "2b",
        "SlitWidth": 0.0302,
        "FrontPitch": 0.054357,
        "FrontOrient": 70.1663,
        "RearPitch": 0.054243,
        "RearOrient": 69.8341,
        "PitchToler": 0.000012,
        "OrientToler": 0.0126,
        "BridgePitch": 1.05,
        "BridgeOrient": 160,
        "BridgeWidth": 0.05
    },
    "20": {
        "Label": "10b",
        "SlitWidth": 0.4793,
        "FrontPitch": 0.951208,
        "FrontOrient": 86.9019,
        "RearPitch": 0.951208,
        "RearOrient": 93.0981,
        "PitchToler": 0.00368,
        "OrientToler": 0.222,
        "BridgePitch": "NA",
        "BridgeOrient": "NA",
        "BridgeWidth": "NA"
    },
    "21": {
        "Label": "8a",
        "SlitWidth": 0.2358,
        "FrontPitch": 0.453678,
        "FrontOrient": 9.7435,
        "RearPitch": 0.477944,
        "RearOrient": 10.2702,
        "PitchToler": 0.000879,
        "OrientToler": 0.108,
        "BridgePitch": 3.02,
        "BridgeOrient": 100,
        "BridgeWidth": 0.05
    },
    "22": {
        "Label": "10c",
        "SlitWidth": 0.4793,
        "FrontPitch": 0.909644,
        "FrontOrient": 28.5192,
        "RearPitch": 0.999045,
        "RearOrient": 31.6264,
        "PitchToler": 0.00368,
        "OrientToler": 0.222,
        "BridgePitch": "NA",
        "BridgeOrient": "NA",
        "BridgeWidth": "NA"
    },
    "23": {
        "Label": "4c",
        "SlitWidth": 0.0586,
        "FrontPitch": 0.110594,
        "FrontOrient": 150.18,
        "RearPitch": 0.111811,
        "RearOrient": 149.818,
        "PitchToler": 0.0000502,
        "OrientToler": 0.0259,
        "BridgePitch": 1.69,
        "BridgeOrient": 60,
        "BridgeWidth": 0.05
    },
    "24": {
        "Label": "7a",
        "SlitWidth": 0.1657,
        "FrontPitch": 0.320259,
        "FrontOrient": 29.4787,
        "RearPitch": 0.33068,
        "RearOrient": 30.5383,
        "PitchToler": 0.00043,
        "OrientToler": 0.0757,
        "BridgePitch": 2.66,
        "BridgeOrient": 120,
        "BridgeWidth": 0.05
    },
    "25": {
        "Label": "4a",
        "SlitWidth": 0.0586,
        "FrontPitch": 0.111198,
        "FrontOrient": 89.638,
        "RearPitch": 0.111198,
        "RearOrient": 90.362,
        "PitchToler": 0.0000502,
        "OrientToler": 0.0259,
        "BridgePitch": 1.1,
        "BridgeOrient": 0,
        "BridgeWidth": 0.05
    },
    "26": {
        "Label": "8b",
        "SlitWidth": 0.2358,
        "FrontPitch": 0.457628,
        "FrontOrient": 131.1413,
        "RearPitch": 0.47345,
        "RearOrient": 128.8192,
        "PitchToler": 0.000879,
        "OrientToler": 0.108,
        "BridgePitch": 2.95,
        "BridgeOrient": 40,
        "BridgeWidth": 0.05
    },
    "27": {
        "Label": "6b",
        "SlitWidth": 0.1168,
        "FrontPitch": 0.230433,
        "FrontOrient": 169.8697,
        "RearPitch": 0.22464,
        "RearOrient": 170.127,
        "PitchToler": 0.00021,
        "OrientToler": 0.0529,
        "BridgePitch": 2.28,
        "BridgeOrient": 80,
        "BridgeWidth": 0.05
    },
    "28": {
        "Label": "7c",
        "SlitWidth": 0.1657,
        "FrontPitch": 0.325344,
        "FrontOrient": 91.0592,
        "RearPitch": 0.325344,
        "RearOrient": 88.9408,
        "PitchToler": 0.00043,
        "OrientToler": 0.0757,
        "BridgePitch": 2.2,
        "BridgeOrient": 0,
        "BridgeWidth": 0.05
    },
    "29": {
        "Label": "3b",
        "SlitWidth": 0.0419,
        "FrontPitch": 0.077921,
        "FrontOrient": 50.1943,
        "RearPitch": 0.07748,
        "RearOrient": 49.8068,
        "PitchToler": 0.0000245,
        "OrientToler": 0.0181,
        "BridgePitch": 1.18,
        "BridgeOrient": 140,
        "BridgeWidth": 0.05
    },
    "30": {
        "Label": "5b",
        "SlitWidth": 0.0825,
        "FrontPitch": 0.160427,
        "FrontOrient": 10.0907,
        "RearPitch": 0.157598,
        "RearOrient": 9.9109,
        "PitchToler": 0.000103,
        "OrientToler": 0.037,
        "BridgePitch": 1.81,
        "BridgeOrient": 100,
        "BridgeWidth": 0.05
    },
    "31": {
        "Label": "6c",
        "SlitWidth": 0.1168,
        "FrontPitch": 0.228493,
        "FrontOrient": 109.301,
        "RearPitch": 0.226482,
        "RearOrient": 110.6929,
        "PitchToler": 0.00021,
        "OrientToler": 0.0529,
        "BridgePitch": 2.07,
        "BridgeOrient": 20,
        "BridgeWidth": 0.05
    },
    "32": {
        "Label": "9c",
        "SlitWidth": 0.336,
        "FrontPitch": 0.682197,
        "FrontOrient": 51.7015,
        "RearPitch": 0.64983,
        "RearOrient": 48.3792,
        "PitchToler": 0.0018,
        "OrientToler": 0.155,
        "BridgePitch": "NA",
        "BridgeOrient": "NA",
        "BridgeWidth": "NA"
    },
    "33": {
        "Label": "dummy",
        "SlitWidth": 0.0302 * 0.5,
        "FrontPitch": 0.054136 * 0.5,
        "FrontOrient": 9.9694,
        "RearPitch": 0.054465 * .5,
        "RearOrient": 10.0308,
        "PitchToler": 0.000012,
        "OrientToler": 0.0126,
        "BridgePitch": 1.13,
        "BridgeOrient": 100,
        "BridgeWidth": 0.05
    },
    '34': {
        "Label": "9c",
        "SlitWidth": 0.5,
        "FrontPitch": 1,
        "FrontOrient": 90,
        "RearPitch": 1,
        "RearOrient": 90,
        "PitchToler": 0,
        "OrientToler": 0,
        "BridgePitch": "NA",
        "BridgeOrient": "NA",
        "BridgeWidth": "NA"
    },
    "units": {
        "SlitWidth": "mm",
        "FrontPitch": "mm",
        "FrontOrient": "deg",
        "RearPitch": "mm",
        "RearOrient": "deg",
        "PitchToler": "mm",
        "OrientToler": "deg",
        "BridgePitch": "mm",
        "BridgeOrient": "deg",
        "BridgeWidth": "mm",
        "AvgOrient": 'deg',
        'AngRes': 'arcsec',
        'Pitch': 'mm',
    },
}
# data from matj
real_grid_parameters = {
    "1": {
        "FrontPitch": 0.07805,
        "FrontOrient": 169.977,
        "FrontPhase": 0.0048,
        "FrontSlitWidth": 0.0457,
        "FrontSlitGradient": 0.0009,
        "FrontRMS": 0.0012,
        "FrontThickness": 0.3538,
        "FrontBridgeWidth": 0.0433,
        "FrontBridgePitch": 1.130299,
        "RearPitch": 0.077388,
        "RearOrient": 170.037,
        "RearPhase": 0.0173,
        "RearSlitWidth": 0.0507,
        "RearSlitGradient": 0.0007,
        "RearRMS": 0.0011,
        "RearThickness": 0.3628,
        "RearBridgeWidth": 0.0398,
        "RearBridgePitch": 1.130199
    },
    "2": {
        "FrontPitch": 0.158102,
        "FrontOrient": 130.406,
        "FrontPhase": 0.1136,
        "FrontSlitWidth": 0.07645,
        "FrontSlitGradient": 0.0008,
        "FrontRMS": 0.0009,
        "FrontThickness": 0.3897,
        "FrontBridgeWidth": 0.0587,
        "FrontBridgePitch": 1.970416,
        "RearPitch": 0.159965,
        "RearOrient": 129.588,
        "RearPhase": 0.1497,
        "RearSlitWidth": 0.0806,
        "RearSlitGradient": 0.0004,
        "RearRMS": 0.0008,
        "RearThickness": 0.3901,
        "RearBridgeWidth": 0.0543,
        "RearBridgePitch": 1.970729
    },
    "3": {
        "FrontPitch": 0.909818,
        "FrontOrient": 151.503,
        "FrontPhase": 0.1114,
        "FrontSlitWidth": 0.4811,
        "FrontSlitGradient": 0.0008,
        "FrontRMS": 0.0014,
        "FrontThickness": 0.4413,
        "FrontBridgeWidth": 0,
        "FrontBridgePitch": 0,
        "RearPitch": 0.999226,
        "RearOrient": 148.373,
        "RearPhase": 0.086,
        "RearSlitWidth": 0.492,
        "RearSlitGradient": 0.0026,
        "RearRMS": 0.0011,
        "RearThickness": 0.421,
        "RearBridgeWidth": 0,
        "RearBridgePitch": 0
    },
    "4": {
        "FrontPitch": 0.46131,
        "FrontOrient": 68.608,
        "FrontPhase": 0.1562,
        "FrontSlitWidth": 0.2352,
        "FrontSlitGradient": 0.0004,
        "FrontRMS": 0.0011,
        "FrontThickness": 0.4171,
        "FrontBridgeWidth": 0.0426,
        "FrontBridgePitch": 3.150334,
        "RearPitch": 0.469697,
        "RearOrient": 71.434,
        "RearPhase": 0.456,
        "RearSlitWidth": 0.2431,
        "RearSlitGradient": 0.0029,
        "RearRMS": 0.001,
        "RearThickness": 0.3922,
        "RearBridgeWidth": 0.0416,
        "RearBridgePitch": 3.150274
    },
    "5": {
        "FrontPitch": 0.110609,
        "FrontOrient": 29.839,
        "FrontPhase": 0.0102,
        "FrontSlitWidth": 0.0566,
        "FrontSlitGradient": 0.0009,
        "FrontRMS": 0.0008,
        "FrontThickness": 0.3813,
        "FrontBridgeWidth": 0.5,
        "FrontBridgePitch": 1.65,
        "RearPitch": 0.111831,
        "RearOrient": 30.18,
        "RearPhase": 0.0497,
        "RearSlitWidth": 0.0623,
        "RearSlitGradient": 0.0005,
        "RearRMS": 0.0009,
        "RearThickness": 0.4082,
        "RearBridgeWidth": 0.0378,
        "RearBridgePitch": 1.690653
    },
    "6": {
        "FrontPitch": 0.15853,
        "FrontOrient": 69.527,
        "FrontPhase": 0.0247,
        "FrontSlitWidth": 0.0741,
        "FrontSlitGradient": 0.0007,
        "FrontRMS": 0.0007,
        "FrontThickness": 0.3924,
        "FrontBridgeWidth": 0.0618,
        "FrontBridgePitch": 1.580188,
        "RearPitch": 0.159539,
        "RearOrient": 70.48,
        "RearPhase": 0.0086,
        "RearSlitWidth": 0.0849,
        "RearSlitGradient": 0.0006,
        "RearRMS": 0.0007,
        "RearThickness": 0.4226,
        "RearBridgeWidth": 0.0582,
        "RearBridgePitch": 1.580039
    },
    "7": {
        "FrontPitch": 0.077594,
        "FrontOrient": 110.252,
        "FrontPhase": 0.0195,
        "FrontSlitWidth": 0.0465,
        "FrontSlitGradient": 0.0019,
        "FrontRMS": 0.0009,
        "FrontThickness": 0.374,
        "FrontBridgeWidth": 0.0422,
        "FrontBridgePitch": 1.050062,
        "RearPitch": 0.077834,
        "RearOrient": 109.754,
        "RearPhase": 0.0388,
        "RearSlitWidth": 0.0534,
        "RearSlitGradient": 0.0012,
        "RearRMS": 0.0007,
        "RearThickness": 0.3896,
        "RearBridgeWidth": 0.0399,
        "RearBridgePitch": 1.050446
    },
    "8": {
        "FrontPitch": 0.32033,
        "FrontOrient": 150.541,
        "FrontPhase": 0.0178,
        "FrontSlitWidth": 0.1589,
        "FrontSlitGradient": 0.0006,
        "FrontRMS": 0.0008,
        "FrontThickness": 0.405,
        "FrontBridgeWidth": 0.0441,
        "FrontBridgePitch": 2.661093,
        "RearPitch": 0.330751,
        "RearOrient": 149.46,
        "RearPhase": 0.3021,
        "RearSlitWidth": 0.1712,
        "RearSlitGradient": 0.001,
        "RearRMS": 0.0009,
        "RearThickness": 0.3805,
        "RearBridgeWidth": 0.0434,
        "RearBridgePitch": 2.660393
    },
    "9": {
        "FrontPitch": "CFL",
        "FrontOrient": "CFL",
        "FrontPhase": "CFL",
        "FrontSlitWidth": "CFL",
        "FrontSlitGradient": "CFL",
        "FrontRMS": "CFL",
        "FrontThickness": "CFL",
        "FrontBridgeWidth": "CFL",
        "FrontBridgePitch": "CFL",
        "RearPitch": "CFL",
        "RearOrient": "CFL",
        "RearPhase": "CFL",
        "RearSlitWidth": "CFL",
        "RearSlitGradient": "CFL",
        "RearRMS": "CFL",
        "RearThickness": "CFL",
        "RearBridgeWidth": "CFL",
        "RearBridgePitch": "CFL"
    },
    "10": {
        "FrontPitch": "BKG",
        "FrontOrient": "BKG",
        "FrontPhase": "BKG",
        "FrontSlitWidth": "BKG",
        "FrontSlitGradient": "BKG",
        "FrontRMS": "BKG",
        "FrontThickness": "BKG",
        "FrontBridgeWidth": "BKG",
        "FrontBridgePitch": "BKG",
        "RearPitch": "BKG",
        "RearOrient": "BKG",
        "RearPhase": "BKG",
        "RearSlitWidth": "BKG",
        "RearSlitGradient": "BKG",
        "RearRMS": "BKG",
        "RearThickness": "BKG",
        "RearBridgeWidth": "BKG",
        "RearBridgePitch": "BKG"
    },
    "11": {
        "FrontPitch": 0.113799,
        "FrontOrient": 150.076,
        "FrontPhase": 0.0147,
        "FrontSlitWidth": 0.0934,
        "FrontSlitGradient": 0.0013,
        "FrontRMS": 0.0011,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": 0.0464,
        "FrontBridgePitch": 1.099888,
        "RearPitch": 0.114224,
        "RearOrient": 149.93,
        "RearPhase": 0.0668,
        "RearSlitWidth": 0.0971,
        "RearSlitGradient": 0.0004,
        "RearRMS": 0.0011,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": 0.0495,
        "RearBridgePitch": 1.100279
    },
    "15": {
        "FrontPitch": 0.229421,
        "FrontOrient": 50.582,
        "FrontPhase": 0.0469,
        "FrontSlitWidth": 0.1094,
        "FrontSlitGradient": 0.0014,
        "FrontRMS": 0.0016,
        "FrontThickness": 0.3819,
        "FrontBridgeWidth": 0.0516,
        "FrontBridgePitch": 1.970634,
        "RearPitch": 0.225653,
        "RearOrient": 49.427,
        "RearPhase": 0.0326,
        "RearSlitWidth": 0.1155,
        "RearSlitGradient": 0.002,
        "RearRMS": 0.0014,
        "RearThickness": 0.3787,
        "RearBridgeWidth": 0.0527,
        "RearBridgePitch": 1.970511
    },
    "16": {
        "FrontPitch": 0.642102,
        "FrontOrient": 170.393,
        "FrontPhase": 0.0152,
        "FrontSlitWidth": 0.3364,
        "FrontSlitGradient": 0.0031,
        "FrontRMS": 0.0014,
        "FrontThickness": 0.4011,
        "FrontBridgeWidth": 0,
        "FrontBridgePitch": 0,
        "RearPitch": 0.691758,
        "RearOrient": 169.609,
        "RearPhase": 0.3612,
        "RearSlitWidth": 0.3451,
        "RearSlitGradient": 0.0021,
        "RearRMS": 0.0011,
        "RearThickness": 0.4053,
        "RearBridgeWidth": 0,
        "RearBridgePitch": 0
    },
    "20": {
        "FrontPitch": 0.951346,
        "FrontOrient": 86.916,
        "FrontPhase": 0.913,
        "FrontSlitWidth": 0.4903,
        "FrontSlitGradient": 0.0017,
        "FrontRMS": 0.0012,
        "FrontThickness": 0.4375,
        "FrontBridgeWidth": 0,
        "FrontBridgePitch": 0,
        "RearPitch": 0.951412,
        "RearOrient": 93.105,
        "RearPhase": 0.2194,
        "RearSlitWidth": 0.492,
        "RearSlitGradient": 0.0039,
        "RearRMS": 0.0014,
        "RearThickness": 0.4052,
        "RearBridgeWidth": 0,
        "RearBridgePitch": 0
    },
    "21": {
        "FrontPitch": 0.453733,
        "FrontOrient": 9.763,
        "FrontPhase": 0.1752,
        "FrontSlitWidth": 0.2286,
        "FrontSlitGradient": 0.0024,
        "FrontRMS": 0.0019,
        "FrontThickness": 0.3819,
        "FrontBridgeWidth": 0.0463,
        "FrontBridgePitch": 3.020667,
        "RearPitch": 0.478018,
        "RearOrient": 10.273,
        "RearPhase": 0.4254,
        "RearSlitWidth": 0.2415,
        "RearSlitGradient": 0.0012,
        "RearRMS": 0.0014,
        "RearThickness": 0.3866,
        "RearBridgeWidth": 0.0436,
        "RearBridgePitch": 3.021032
    },
    "22": {
        "FrontPitch": 0.909875,
        "FrontOrient": 28.534,
        "FrontPhase": 0.7453,
        "FrontSlitWidth": 0.4781,
        "FrontSlitGradient": 0.0009,
        "FrontRMS": 0.0027,
        "FrontThickness": 0.4153,
        "FrontBridgeWidth": 0,
        "FrontBridgePitch": 0,
        "RearPitch": 0.999212,
        "RearOrient": 31.621,
        "RearPhase": 0.2162,
        "RearSlitWidth": 0.4878,
        "RearSlitGradient": 0.0026,
        "RearRMS": 0.0016,
        "RearThickness": 0.4144,
        "RearBridgeWidth": 0,
        "RearBridgePitch": 0
    },
    "23": {
        "FrontPitch": 0.110621,
        "FrontOrient": 150.188,
        "FrontPhase": 0.0762,
        "FrontSlitWidth": 0.0555,
        "FrontSlitGradient": 0.001,
        "FrontRMS": 0.0009,
        "FrontThickness": 0.3714,
        "FrontBridgeWidth": 0.0356,
        "FrontBridgePitch": 1.690305,
        "RearPitch": 0.111829,
        "RearOrient": 149.804,
        "RearPhase": 0.038,
        "RearSlitWidth": 0.0624,
        "RearSlitGradient": 0.0009,
        "RearRMS": 0.0009,
        "RearThickness": 0.3947,
        "RearBridgeWidth": 0.0391,
        "RearBridgePitch": 1.69002
    },
    "24": {
        "FrontPitch": 0.320329,
        "FrontOrient": 29.494,
        "FrontPhase": 0.192,
        "FrontSlitWidth": 0.1555,
        "FrontSlitGradient": 0.001,
        "FrontRMS": 0.0011,
        "FrontThickness": 0.4183,
        "FrontBridgeWidth": 0.0508,
        "FrontBridgePitch": 2.660021,
        "RearPitch": 0.330741,
        "RearOrient": 30.534,
        "RearPhase": 0.2552,
        "RearSlitWidth": 0.1632,
        "RearSlitGradient": 0.0005,
        "RearRMS": 0.001,
        "RearThickness": 0.4123,
        "RearBridgeWidth": 0.0467,
        "RearBridgePitch": 2.660331
    },
    "25": {
        "FrontPitch": 0.111218,
        "FrontOrient": 89.65,
        "FrontPhase": 0.0078,
        "FrontSlitWidth": 0.0575,
        "FrontSlitGradient": 0.0009,
        "FrontRMS": 0.0006,
        "FrontThickness": 0.391,
        "FrontBridgeWidth": 0.0386,
        "FrontBridgePitch": 1.100597,
        "RearPitch": 0.111216,
        "RearOrient": 90.354,
        "RearPhase": 0.1018,
        "RearSlitWidth": 0.0626,
        "RearSlitGradient": 0.0008,
        "RearRMS": 0.0005,
        "RearThickness": 0.3697,
        "RearBridgeWidth": 0.042,
        "RearBridgePitch": 1.09966
    },
    "26": {
        "FrontPitch": 0.457701,
        "FrontOrient": 131.16,
        "FrontPhase": 0.1632,
        "FrontSlitWidth": 0.2307,
        "FrontSlitGradient": 0.0044,
        "FrontRMS": 0.0014,
        "FrontThickness": 0.3609,
        "FrontBridgeWidth": 0.0492,
        "FrontBridgePitch": 2.9513,
        "RearPitch": 0.473501,
        "RearOrient": 128.82,
        "RearPhase": 0.3551,
        "RearSlitWidth": 0.241,
        "RearSlitGradient": 0.0057,
        "RearRMS": 0.0015,
        "RearThickness": 0.3879,
        "RearBridgeWidth": 0.0399,
        "RearBridgePitch": 2.949872
    },
    "27": {
        "FrontPitch": 0.23049,
        "FrontOrient": 169.887,
        "FrontPhase": 0.0272,
        "FrontSlitWidth": 0.1039,
        "FrontSlitGradient": 0.0017,
        "FrontRMS": 0.0016,
        "FrontThickness": 0.3476,
        "FrontBridgeWidth": 0.0568,
        "FrontBridgePitch": 2.280569,
        "RearPitch": 0.224674,
        "RearOrient": 170.124,
        "RearPhase": 0.2222,
        "RearSlitWidth": 0.1155,
        "RearSlitGradient": 0.0024,
        "RearRMS": 0.0011,
        "RearThickness": 0.3676,
        "RearBridgeWidth": 0.0567,
        "RearBridgePitch": 2.279257
    },
    "28": {
        "FrontPitch": 0.32543,
        "FrontOrient": 91.078,
        "FrontPhase": 0.2984,
        "FrontSlitWidth": 0.1679,
        "FrontSlitGradient": 0.0006,
        "FrontRMS": 0.0013,
        "FrontThickness": 0.4149,
        "FrontBridgeWidth": 0.0554,
        "FrontBridgePitch": 2.200088,
        "RearPitch": 0.325412,
        "RearOrient": 88.938,
        "RearPhase": 0.058,
        "RearSlitWidth": 0.171,
        "RearSlitGradient": 0.0014,
        "RearRMS": 0.0015,
        "RearThickness": 0.3852,
        "RearBridgeWidth": 0.0521,
        "RearBridgePitch": 2.200617
    },
    "29": {
        "FrontPitch": 0.077934,
        "FrontOrient": 50.203,
        "FrontPhase": 0.0628,
        "FrontSlitWidth": 0.046,
        "FrontSlitGradient": 0.0011,
        "FrontRMS": 0.0009,
        "FrontThickness": 0.3597,
        "FrontBridgeWidth": 0.0446,
        "FrontBridgePitch": 1.180051,
        "RearPitch": 0.077494,
        "RearOrient": 49.798,
        "RearPhase": 0.0494,
        "RearSlitWidth": 0.0513,
        "RearSlitGradient": 0.0005,
        "RearRMS": 0.0007,
        "RearThickness": 0.3546,
        "RearBridgeWidth": 0.0357,
        "RearBridgePitch": 1.180175
    },
    "30": {
        "FrontPitch": 0.16043,
        "FrontOrient": 10.117,
        "FrontPhase": 0.0749,
        "FrontSlitWidth": 0.0772,
        "FrontSlitGradient": 0.0007,
        "FrontRMS": 0.0011,
        "FrontThickness": 0.3903,
        "FrontBridgeWidth": 0.059,
        "FrontBridgePitch": 1.810433,
        "RearPitch": 0.157633,
        "RearOrient": 9.911,
        "RearPhase": 0.0927,
        "RearSlitWidth": 0.0852,
        "RearSlitGradient": 0.0008,
        "RearRMS": 0.001,
        "RearThickness": 0.3989,
        "RearBridgeWidth": 0.0615,
        "RearBridgePitch": 1.810039
    },
    "31": {
        "FrontPitch": 0.228531,
        "FrontOrient": 109.323,
        "FrontPhase": 0.0969,
        "FrontSlitWidth": 0.119,
        "FrontSlitGradient": 0.0006,
        "FrontRMS": 0.001,
        "FrontThickness": 0.3838,
        "FrontBridgeWidth": 0.0595,
        "FrontBridgePitch": 2.070182,
        "RearPitch": 0.226511,
        "RearOrient": 110.694,
        "RearPhase": 0.1825,
        "RearSlitWidth": 0.115,
        "RearSlitGradient": 0.001,
        "RearRMS": 0.0013,
        "RearThickness": 0.365,
        "RearBridgeWidth": 0.0541,
        "RearBridgePitch": 2.070283
    },
    "32": {
        "FrontPitch": 0.682253,
        "FrontOrient": 51.714,
        "FrontPhase": 0.4855,
        "FrontSlitWidth": 0.3384,
        "FrontSlitGradient": 0.0018,
        "FrontRMS": 0.0032,
        "FrontThickness": 0.398,
        "FrontBridgeWidth": 0,
        "FrontBridgePitch": 0,
        "RearPitch": 0.649947,
        "RearOrient": 48.378,
        "RearPhase": 0.3333,
        "RearSlitWidth": 0.3421,
        "RearSlitGradient": 0.0034,
        "RearRMS": 0.0012,
        "RearThickness": 0.3884,
        "RearBridgeWidth": 0,
        "RearBridgePitch": 0
    },
    "12a": {
        "FrontPitch": 0.108817,
        "FrontOrient": 129.883,
        "FrontPhase": 0.059,
        "FrontSlitWidth": 0.0795,
        "FrontSlitGradient": 0.0014,
        "FrontRMS": 0.001,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": 0.044,
        "FrontBridgePitch": 1.180036,
        "RearPitch": 0.108394,
        "RearOrient": 130.131,
        "RearPhase": 0.0542,
        "RearSlitWidth": 0.0813,
        "RearSlitGradient": 0.0003,
        "RearRMS": 0.001,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": 0.0462,
        "RearBridgePitch": 1.180239
    },
    "12b": {
        "FrontPitch": 0.108825,
        "FrontOrient": 129.879,
        "FrontPhase": 0.0032,
        "FrontSlitWidth": 0.0835,
        "FrontSlitGradient": 0.0008,
        "FrontRMS": 0.001,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": "",
        "FrontBridgePitch": "",
        "RearPitch": 0.108406,
        "RearOrient": 130.131,
        "RearPhase": 0.1026,
        "RearSlitWidth": 0.081,
        "RearSlitGradient": 0.0005,
        "RearRMS": 0.001,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": "",
        "RearBridgePitch": ""
    },
    "13a": {
        "FrontPitch": 0.113998,
        "FrontOrient": 90.143,
        "FrontPhase": 0.0533,
        "FrontSlitWidth": 0.0919,
        "FrontSlitGradient": 0.0019,
        "FrontRMS": 0.0009,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": "",
        "FrontBridgePitch": "",
        "RearPitch": 0.113995,
        "RearOrient": 89.865,
        "RearPhase": 0.0362,
        "RearSlitWidth": 0.0915,
        "RearSlitGradient": 0.0007,
        "RearRMS": 0.0008,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": "",
        "RearBridgePitch": ""
    },
    "13b": {
        "FrontPitch": 0.114008,
        "FrontOrient": 90.137,
        "FrontPhase": 0.0121,
        "FrontSlitWidth": 0.0867,
        "FrontSlitGradient": 0.0008,
        "FrontRMS": 0.0008,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": "",
        "FrontBridgePitch": "",
        "RearPitch": 0.114015,
        "RearOrient": 89.862,
        "RearPhase": 0.0658,
        "RearSlitWidth": 0.0833,
        "RearSlitGradient": 0.0009,
        "RearRMS": 0.0009,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": "",
        "RearBridgePitch": ""
    },
    "14c": {
        "FrontPitch": 0.674276,
        "FrontOrient": 107.955,
        "FrontPhase": 0.0477,
        "FrontSlitWidth": 0.3377,
        "FrontSlitGradient": 0.0006,
        "FrontRMS": 0.0016,
        "FrontThickness": 0.4024,
        "FrontBridgeWidth": 0,
        "FrontBridgePitch": 0,
        "RearPitch": 0.657124,
        "RearOrient": 112.013,
        "RearPhase": 0.2675,
        "RearSlitWidth": 0.3455,
        "RearSlitGradient": 0.0031,
        "RearRMS": 0.0013,
        "RearThickness": 0.3977,
        "RearBridgeWidth": 0,
        "RearBridgePitch": 0
    },
    "17a": {
        "FrontPitch": 0.108278,
        "FrontOrient": 9.995,
        "FrontPhase": 0.1656,
        "FrontSlitWidth": 0.0839,
        "FrontSlitGradient": 0.0007,
        "FrontRMS": 0.0012,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": 0.0544,
        "FrontBridgePitch": 1.130375,
        "RearPitch": 0.10894,
        "RearOrient": 10.031,
        "RearPhase": 0.1056,
        "RearSlitWidth": 0.0861,
        "RearSlitGradient": 0.0004,
        "RearRMS": 0.001,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": 0.0594,
        "RearBridgePitch": 1.129875
    },
    "17b": {
        "FrontPitch": 0.108286,
        "FrontOrient": 9.99,
        "FrontPhase": 0.0569,
        "FrontSlitWidth": 0.0852,
        "FrontSlitGradient": 0.0008,
        "FrontRMS": 0.0011,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": "",
        "FrontBridgePitch": "",
        "RearPitch": 0.108958,
        "RearOrient": 10.034,
        "RearPhase": 0.0523,
        "RearSlitWidth": 0.0845,
        "RearSlitGradient": 0.0005,
        "RearRMS": 0.0009,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": "",
        "RearBridgePitch": ""
    },
    "18a": {
        "FrontPitch": 0.113806,
        "FrontOrient": 29.957,
        "FrontPhase": 0.0366,
        "FrontSlitWidth": 0.0881,
        "FrontSlitGradient": 0.002,
        "FrontRMS": 0.0013,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": 0.0469,
        "FrontBridgePitch": 1.100317,
        "RearPitch": 0.114231,
        "RearOrient": 30.058,
        "RearPhase": 0.0923,
        "RearSlitWidth": 0.0954,
        "RearSlitGradient": 0.0007,
        "RearRMS": 0.0013,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": 0.0506,
        "RearBridgePitch": 1.100059
    },
    "18b": {
        "FrontPitch": 0.113801,
        "FrontOrient": 29.954,
        "FrontPhase": 0.106,
        "FrontSlitWidth": 0.0929,
        "FrontSlitGradient": 0.0007,
        "FrontRMS": 0.0011,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": "",
        "FrontBridgePitch": "",
        "RearPitch": 0.11422,
        "RearOrient": 30.063,
        "RearPhase": 0.0608,
        "RearSlitWidth": 0.0941,
        "RearSlitGradient": 0.0006,
        "RearRMS": 0.0011,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": "",
        "RearBridgePitch": ""
    },
    "18c": {
        "FrontPitch": 0.113808,
        "FrontOrient": 29.956,
        "FrontPhase": 0.071,
        "FrontSlitWidth": 0.0929,
        "FrontSlitGradient": 0.0011,
        "FrontRMS": 0.0011,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": "",
        "FrontBridgePitch": "",
        "RearPitch": 0.114238,
        "RearOrient": 30.06,
        "RearPhase": 0.0166,
        "RearSlitWidth": 0.0919,
        "RearSlitGradient": 0.0014,
        "RearRMS": 0.0011,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": "",
        "RearBridgePitch": ""
    },
    "19a": {
        "FrontPitch": 0.108729,
        "FrontOrient": 70.188,
        "FrontPhase": 0.0098,
        "FrontSlitWidth": 0.0833,
        "FrontSlitGradient": 0.0012,
        "FrontRMS": 0.0007,
        "FrontThickness": "Non-recov.",
        "FrontBridgeWidth": "",
        "FrontBridgePitch": "",
        "RearPitch": 0.108493,
        "RearOrient": 69.834,
        "RearPhase": 0.0257,
        "RearSlitWidth": 0.0814,
        "RearSlitGradient": 0.0009,
        "RearRMS": 0.0009,
        "RearThickness": "Non-recov.",
        "RearBridgeWidth": "",
        "RearBridgePitch": ""
    }
}
detector_center_coords = {
    "1": {
        "x": -62.5,
        "y": 36.5
    },
    "2": {
        "x": -62.5,
        "y": 13.5
    },
    "3": {
        "x": -62.5,
        "y": -13.5
    },
    "4": {
        "x": -62.5,
        "y": -36.5
    },
    "5": {
        "x": -37.5,
        "y": 59.5
    },
    "6": {
        "x": -37.5,
        "y": 36.5
    },
    "7": {
        "x": -37.5,
        "y": 13.5
    },
    "8": {
        "x": -37.5,
        "y": -13.5
    },
    "9": {
        "x": -37.5,
        "y": -36.5
    },
    "10": {
        "x": -37.5,
        "y": -59.5
    },
    "11": {
        "x": -12.5,
        "y": 73.5
    },
    "12": {
        "x": -12.5,
        "y": 50.5
    },
    "13": {
        "x": -12.5,
        "y": 27.5
    },
    "14": {
        "x": -12.5,
        "y": -27.5
    },
    "15": {
        "x": -12.5,
        "y": -50.5
    },
    "16": {
        "x": -12.5,
        "y": -73.5
    },
    "17": {
        "x": 12.5,
        "y": 73.5
    },
    "18": {
        "x": 12.5,
        "y": 50.5
    },
    "19": {
        "x": 12.5,
        "y": 27.5
    },
    "20": {
        "x": 12.5,
        "y": -27.5
    },
    "21": {
        "x": 12.5,
        "y": -50.5
    },
    "22": {
        "x": 12.5,
        "y": -73.5
    },
    "23": {
        "x": 37.5,
        "y": 59.5
    },
    "24": {
        "x": 37.5,
        "y": 36.5
    },
    "25": {
        "x": 37.5,
        "y": 13.5
    },
    "26": {
        "x": 37.5,
        "y": -13.5
    },
    "27": {
        "x": 37.5,
        "y": -36.5
    },
    "28": {
        "x": 37.5,
        "y": -59.5
    },
    "29": {
        "x": 62.5,
        "y": 36.5
    },
    "30": {
        "x": 62.5,
        "y": 13.5
    },
    "31": {
        "x": 62.5,
        "y": -13.5
    },
    "32": {
        "x": 62.5,
        "y": -36.5
    }
}
cfl_aperture_coords = {
    'outer': [(-14.3, -13.45), (-14.3, 13.45), (14.3, 13.45), (14.3, -13.45)],
    'top': [(-4.4, 3.45), (-4.4, 10.0), (4.4, 10.0), (4.4, 3.45)],
    'bottom': [(-4.4, -10.0), (-4.4, -3.45), (4.4, -3.45), (4.4, -10.0)],
    'left_top': [(-11.0, 3.45), (-11.0, 10.0), (-9.9, 10.0), (-9.9, 3.45)],
    'left_bottom': [(-11.0, -10.0), (-11.0, -3.45), (-9.9, -3.45),
                    (-9.9, -10.0)],
    'right_top': [(9.9, 3.45), (9.9, 10.0), (11.0, 10.0), (11.0, 3.45)],
    'right_bottom': [(9.9, -10.0), (9.9, -3.45), (11.0, -3.45), (11.0, -10.0)]
}

r_front_detector = 550 + 47  # measured from CAD
r_rear_detector = 47
frame_vertices = {
    'front': [(-11, -10), (-11, 10), (11, 10), (11, -10), (-11, -10)],
    'rear': [(-6.5, -6.5), (-6.5, 6.5), (6.5, 6.5), (6.5, -6.5), (-6.5, -6.5)]
}
grid_dim = {'front': (22, 20), 'rear': (13, 13)}  # grid dimemsions
grid_z = {
    'det': 0,
    'rear': r_rear_detector,
    'front': r_front_detector
}  # grid z coordinates


ebin_low_edges = np.array([
    0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 25, 28, 32,
    36, 40, 45, 50, 56, 63, 70, 76, 84, 100, 120, 150, math.inf
])
ebins = np.vstack((ebin_low_edges[0:-1], ebin_low_edges[1:])).T

detector_ids_in_trigger_accumulators = np.array(
    [[1, 2], [6, 7], [5, 11], [12, 13], [14, 15], [10, 16], [8, 9], [3, 4],
     [31, 32], [26, 27], [22, 28], [20, 21], [18, 19], [17, 23], [24, 25],
     [29, 30]]) - 1
# detector ids of in trigger accounumator
detector_group_map = np.array([
    0, 0, 7, 7, 2, 1, 1, 6, 6, 5, 2, 3, 3, 4, 4, 5, 13, 12, 12, 11, 11, 10, 13,
    14, 14, 9, 9, 10, 15, 15, 8, 8
])

detector_pairs = {
    0: 1,
    5: 6,
    4: 10,
    11: 12,
    13: 14,
    9: 15,
    7: 8,
    2: 3,
    30: 31,
    25: 26,
    21: 27,
    19: 20,
    17: 18,
    16: 22,
    23: 24,
    28: 29,
    1: 0,
    6: 5,
    10: 4,
    12: 11,
    14: 13,
    15: 9,
    8: 7,
    3: 2,
    31: 30,
    26: 25,
    27: 21,
    20: 19,
    18: 17,
    22: 16,
    24: 23,
    29: 28
}

QL_LC_energy_slicers = [
    slice(1, 7),
    slice(7, 12),
    slice(12, 17),
    slice(17, 23),
    slice(23, 28)
]
# energy slicer
DETECTOR_GROUPS = [[1, 2], [6, 7], [5, 11], [12, 13], [14, 15], [10, 16],
                   [8, 9], [3, 4], [31, 32], [26, 27], [22, 28], [20, 21],
                   [18, 19], [17, 23], [24, 25], [29, 30]]
DET_SIBLINGS = {
    0: 1,
    1: 0,
    5: 6,
    6: 5,
    4: 10,
    10: 4,
    11: 12,
    12: 11,
    13: 14,
    14: 13,
    9: 15,
    15: 9,
    7: 8,
    8: 7,
    2: 3,
    3: 2,
    30: 31,
    31: 30,
    25: 26,
    26: 25,
    21: 27,
    27: 21,
    19: 20,
    20: 19,
    17: 18,
    18: 17,
    16: 22,
    22: 16,
    23: 24,
    24: 23,
    28: 29,
    29: 28
}

DET_ID_TO_TRIG_INDEX= {
    0: 0,
    1: 0,
    2: 7,
    3: 7,
    4: 2,
    5: 1,
    6: 1,
    7: 6,
    8: 6,
    9: 5,
    10: 2,
    11: 3,
    12: 3,
    13: 4,
    14: 4,
    15: 5,
    16: 13,
    17: 12,
    18: 12,
    19: 11,
    20: 11,
    21: 10,
    22: 13,
    23: 14,
    24: 14,
    25: 9,
    26: 9,
    27: 10,
    28: 15,
    29: 15,
    30: 8,
    31: 8
}


def detector_id_to_trigger_index(i):
    return DET_ID_TO_TRIG_INDEX[i]


def get_detector_in_same_group(idx):
    """Get detector index in the same group
    Args:
        idx: int
            detector id, detector id range: [0,31]
    Returns
        idx: int
            ID of the detector in the same group
    """
    return detector_pairs.get(idx, None)


def get_trigger_index(idx: int):
    w = np.where(detector_ids_in_trigger_accumulators == idx)
    return w[0][0]


def get_trigger_acc_detector_ids():
    return detector_ids_in_trigger_accumulators


def get_sci_ebins(a, b):
    low = np.where(ebin_low_edges == a)[0][0]
    up = np.where(ebin_low_edges == b)[0][0] - 1

    return (low, up)

def get_spectrogram_energy_bins(elow, ehigh, eunit):
    """
    get spectrogram energy bands of science bins
    """
    eunit += 1
    nbins=int((ehigh-elow+1)/eunit)
 
    ebins=[  (ebin_low_edges[int(elow+i*eunit)], ebin_low_edges[int(elow+(i+1)*eunit)])  for i in range(nbins)]

    return ebins

