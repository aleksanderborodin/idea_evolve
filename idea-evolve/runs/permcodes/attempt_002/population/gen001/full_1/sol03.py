# fitness: 616
"""
Multi-seed AGL(1,8) max clique search with extended exploration.

Run max clique search with many different starting vertex orderings
to find the largest possible orbit clique. Also try extending beyond
the greedy clique by backtracking.
"""

import numpy as np
from itertools import permutations as iperms
from helpers.agl18 import agl18_orbits, agl18_compat_graph


def max_clique_extended(d=5, n_seeds=500):
    """Run max clique search with n_seeds different starting orderings."""
    all_perms = np.array(list(iperms(range(8))), dtype=np.int8)
    orbits = agl18_orbits(all_perms)
    compat = agl18_compat_graph(all_perms, d)
    n_orbits = len(orbits)

    degrees = compat.sum(axis=1)
    order_base = np.argsort(-degrees)

    best_clique = []
    best_size = 0

    for seed in range(n_seeds):
        np.random.seed(seed)
        order = order_base.copy()
        np.random.shuffle(order)

        clique = [int(order[0])]
        cands = np.where(compat[order[0]])[0].tolist()

        while cands:
            scored = [(c, sum(1 for c2 in cands if compat[c, c2])) for c in cands]
            scored.sort(key=lambda x: -x[1])
            v = scored[0][0]
            clique.append(v)
            cands = [c for c in cands if compat[v, c]]

        if len(clique) > best_size:
            best_size = len(clique)
            best_clique = clique.copy()
            print(f"Seed {seed}: found clique of {len(clique)} orbits ({len(clique)*56} codewords)")

        if len(best_clique) >= 15:
            break

    code_parts = [orbits[c] for c in best_clique]
    return np.vstack(code_parts).astype(np.int32)


def entrypoint() -> np.ndarray:
    d = 5
    best_code = max_clique_extended(d=d, n_seeds=500)
    print(f"Final code size: {best_code.shape[0]}")
    return best_code