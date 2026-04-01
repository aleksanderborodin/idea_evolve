# fitness: 616
"""
AGL(1,8) orbit clique code. Result: 616 codewords. Code is maximal (0 compatible perms).
"""
import numpy as np
from helpers.agl18 import agl18_max_clique_code

def entrypoint():
    return agl18_max_clique_code(d=5).astype(np.int32)
