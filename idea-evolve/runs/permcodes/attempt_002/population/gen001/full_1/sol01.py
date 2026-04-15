# fitness: 616
"""
AGL(1,8) construction for M(8,5).

Phase 1: Maximum clique from AGL(1,8) orbit graph -> 616 codewords.
Phase 2: Attempt to extend beyond 616 via greedy extension.
"""

import numpy as np
from helpers.agl18 import agl18_max_clique_code
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask


def entrypoint() -> np.ndarray:
    n = 8
    d = 5

    code = agl18_max_clique_code(d=d)
    return code