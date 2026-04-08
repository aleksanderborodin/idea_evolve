# fitness: 104
"""
104-mark Sidon set from Rokicki-Dogon "Possibly Optimal Golomb Rulers" database.
Source: cube20.org/golomb, rulers-all-00 file.
Entry: marks=104, span=9581, type=pp (Singer projective plane), q=103, multiplier=400.

Note: This uses multiplier=400 applied to the Singer q=103 set — this is why
previous pipeline attempts with Singer q=103 (multiplier=1) scored only 102.
The correct multiplier is essential for achieving 104.
"""


def entrypoint():
    return [
        0, 111, 246, 266, 373, 453, 455, 534, 585, 807, 871, 912, 1009, 1013,
        1187, 1418, 1454, 1508, 1516, 1668, 1708, 1854, 2115, 2180, 2342,
        2508, 2540, 2593, 2712, 2737, 2804, 2972, 3152, 3166, 3208, 3280,
        3329, 3445, 3629, 3690, 3717, 3785, 3932, 3960, 3961, 4352, 4359,
        4510, 4540, 4555, 4639, 4644, 4663, 4896, 4922, 5130, 5232, 5506,
        5615, 5670, 5701, 5841, 5880, 5917, 5990, 6000, 6023, 6034, 6523,
        6545, 6728, 6744, 6929, 6967, 7025, 7042, 7274, 7280, 7326, 7419,
        7493, 7543, 7556, 7643, 7713, 7784, 7861, 8109, 8156, 8433, 8490,
        8499, 8511, 8559, 8602, 8925, 8960, 9019, 9150, 9272, 9275, 9390,
        9408, 9581
    ]
