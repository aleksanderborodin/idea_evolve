# fitness: 616
"""
Exhaustive greedy max-clique search on the AGL(1,8) orbit graph.

The helper's agl18_max_clique_code() tries only 50 starting vertices and
stops at 11 orbits. We try ALL 720 starting vertices with two orderings:
  1. Standard greedy (most neighbors)
  2. Anti-greedy (fewest neighbors — avoids greedy traps)

If any run finds 12+ orbits, we get 672+ codewords.

After finding the best orbit clique, also tries partial-orbit extension:
drop one AGL orbit, greedily add individual permutations (not whole orbits).
"""

import numpy as np
from helpers.agl18 import agl18_orbits, agl18_compat_graph
from itertools import permutations as iperms


def _greedy_clique(compat, start, anti=False):
    n = len(compat)
    clique = [start]
    cands = list(np.where(compat[start])[0])
    while cands:
        scored = [(c, sum(1 for c2 in cands if compat[c, c2])) for c in cands]
        if anti:
            scored.sort(key=lambda x: x[1])   # fewest neighbors
        else:
            scored.sort(key=lambda x: -x[1])  # most neighbors
        v = scored[0][0]
        clique.append(v)
        cands = [c for c in cands if compat[v, c]]
    return clique


def entrypoint():
    print("Building AGL(1,8) orbit data...")
    all_perms = np.array(list(iperms(range(8))), dtype=np.int8)
    orbits = agl18_orbits(all_perms)
    n_orbits = len(orbits)
    print(f"  {n_orbits} orbits")

    print("Building orbit compatibility graph...")
    compat = agl18_compat_graph(all_perms, d=5)
    print(f"  Done. Avg degree: {compat.sum(axis=1).mean():.1f}")

    degrees = compat.sum(axis=1)
    order = np.argsort(-degrees)  # high-degree first

    best_clique = []

    print(f"Searching all {n_orbits} starting vertices (2 strategies each)...")
    for trial, sv in enumerate(order):
        for anti in [False, True]:
            clique = _greedy_clique(compat, int(sv), anti=anti)
            if len(clique) > len(best_clique):
                best_clique = clique
                strat = "anti" if anti else "dense"
                print(f"  [trial {trial}] New best: {len(clique)} orbits = {len(clique)*56} perms ({strat}, sv={sv})")

    print(f"\nBest orbit clique: {len(best_clique)} orbits = {len(best_clique)*56} codewords")

    # Build code from best clique
    code_parts = [orbits[c] for c in best_clique]
    full_code = np.vstack(code_parts).astype(np.int32)

    # Partial-orbit extension: drop last orbit, add individual perms
    if len(best_clique) >= 2:
        reduced_parts = [orbits[c] for c in best_clique[:-1]]
        reduced_code = np.vstack(reduced_parts).astype(np.int32)
        n_reduced = len(reduced_code)
        print(f"\nPartial extension from {n_reduced}-perm code...")

        from helpers.compat import build_bucket_ids, fast_compatible_mask
        bucket_ids = build_bucket_ids(all_perms, n=8, d=5)
        perm_to_idx = {tuple(p.tolist()): i for i, p in enumerate(all_perms)}
        code_idx = np.array([perm_to_idx[tuple(r.tolist())] for r in reduced_code], dtype=np.int32)

        compat_mask = fast_compatible_mask(code_idx, bucket_ids)
        compat_idx = list(np.where(compat_mask)[0])
        print(f"  Compatible perms with {n_reduced}-code: {len(compat_idx)}")

        added = 0
        while compat_idx:
            chosen = compat_idx[0]
            code_idx = np.append(code_idx, chosen)
            new_mask = fast_compatible_mask(np.array([chosen], dtype=np.int32), bucket_ids)
            compat_idx = [idx for idx in compat_idx[1:] if new_mask[idx]]
            added += 1

        extended = all_perms[code_idx].astype(np.int32)
        print(f"  Extended: {len(extended)} codewords (+{added} perms vs {n_reduced})")

        if len(extended) > len(full_code):
            print(f"  Extension wins: {len(extended)} > {len(full_code)}")
            return extended

    return full_code
