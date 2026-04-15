# fitness: 616
"""
Extension attempt beyond AGL(1,8) 616 clique.

Strategy: Find permutations outside the 616-code that are compatible
with all 616 codewords, then greedily add them.
"""

import numpy as np
from helpers.agl18 import agl18_max_clique_code
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask


def entrypoint() -> np.ndarray:
    n = 8
    d = 5

    code = agl18_max_clique_code(d=d)
    code_set = set(map(tuple, code.tolist()))

    all_perms = build_all_perms(n)
    bucket_ids = build_bucket_ids(all_perms)

    code_indices = np.array([i for i, p in enumerate(all_perms) if tuple(p.tolist()) in code_set])

    compat_mask = fast_compatible_mask(code_indices, bucket_ids)
    compat_mask[code_indices] = False
    extension_candidates = all_perms[compat_mask]

    current_code = code.tolist()
    current_indices = code_indices.tolist()

    for candidate in extension_candidates:
        cand_idx = np.where(np.all(all_perms == candidate, axis=1))[0][0]
        new_mask = fast_compatible_mask(np.array(current_indices), bucket_ids)
        new_mask[current_indices] = False
        if new_mask[cand_idx]:
            current_code.append(candidate.tolist())
            current_indices.append(cand_idx)

    return np.array(current_code, dtype=np.int32)