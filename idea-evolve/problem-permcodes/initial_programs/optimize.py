# fitness: 0
"""
Baseline greedy construction for M(8,5).

Strategy: Start with identity permutation, greedily add permutations
that maintain minimum Hamming distance >= 5. Uses random restarts
to find a good initial code.
"""

import numpy as np
from itertools import permutations


def entrypoint() -> np.ndarray:
    n = 8
    d = 5

    np.random.seed(42)

    # Generate all permutations of {0,...,7}
    all_perms = np.array(list(permutations(range(n))), dtype=np.int32)
    N = len(all_perms)  # 40320

    best_code = None
    best_size = 0

    # Multiple greedy attempts with different starting permutations
    for attempt in range(20):
        # Shuffle order for greedy selection
        rng = np.random.RandomState(42 + attempt)
        order = rng.permutation(N)

        code = [all_perms[order[0]]]

        for idx in order[1:]:
            candidate = all_perms[idx]
            # Check distance to all existing codewords
            code_arr = np.array(code)
            dists = np.sum(candidate != code_arr, axis=1)
            if np.all(dists >= d):
                code.append(candidate)

        if len(code) > best_size:
            best_size = len(code)
            best_code = np.array(code)

    return best_code
