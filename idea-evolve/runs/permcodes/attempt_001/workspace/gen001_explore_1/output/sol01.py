# fitness: 616
"""
AGL(1,8) orbit clique (616 codewords).

Uses the standard AGL(1,8) construction: 11 orbits × 56 permutations = 616.
This code is MAXIMAL: no additional permutation can be added while maintaining d≥5.
The code is NOT necessarily MAXIMUM (there might be codes with >616 perms).

Key finding: the AGL(1,8) 616-code is already saturated — 0 compatible perms outside it.
"""

import numpy as np
from helpers.agl18 import agl18_max_clique_code


def entrypoint():
    return agl18_max_clique_code(d=5)
