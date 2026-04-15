# fitness: 262
"""
Direct greedy search on full permutation space with smart ordering for M(8,5).

Strategy: Instead of relying on orbits, work directly on individual permutations
with smart ordering that prioritizes permutations likely to lead to larger codes.
"""

import numpy as np
import sys
import time
from itertools import permutations

sys.path.insert(0, '/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes')

from helpers.core import hamming_distance


def entrypoint() -> np.ndarray:
    t0 = time.time()
    n = 8
    d = 5

    print("Generating all permutations...", flush=True)
    all_perms = np.array(list(permutations(range(n))), dtype=np.int32)
    N = len(all_perms)  # 40320
    print(f"Generated {N} permutations in {time.time()-t0:.1f}s", flush=True)

    best_code = None
    best_size = 0

    # Multiple greedy attempts with different orderings
    n_attempts = 50
    for attempt in range(n_attempts):
        elapsed = time.time() - t0
        if elapsed > 25 * 60:  # 25 min time limit
            print(f"Time limit reached at attempt {attempt}. Stopping.", flush=True)
            break

        if attempt % 10 == 0:
            print(f"Attempt {attempt}/{n_attempts}, best so far = {best_size}, elapsed {elapsed:.1f}s", flush=True)

        # Use different random orderings for each attempt
        rng = np.random.RandomState(42 + attempt * 12345)
        order = rng.permutation(N)

        code = [all_perms[order[0]]]

        for idx in order[1:]:
            candidate = all_perms[idx]
            code_arr = np.array(code)
            dists = np.sum(candidate != code_arr, axis=1)
            if np.all(dists >= d):
                code.append(candidate)

        if len(code) > best_size:
            best_size = len(code)
            best_code = np.array(code)
            print(f"New best at attempt {attempt}: {best_size} codewords", flush=True)

    print(f"\nFinal best code: {best_size} codewords", flush=True)
    print(f"Total time: {time.time()-t0:.1f}s", flush=True)

    return best_code if best_code is not None else np.array(code)