# fitness: 616
"""
Mixed individual-permutation extension of AGL(1,8) orbit clique for M(8,5).

Strategy:
1. Find the best orbit clique (11 orbits → 616 codewords)
2. Search for individual permutations NOT in those orbits that are
   still compatible with ALL 616 orbit-based codewords
3. Even adding 1 extra permutation beats the pure orbit construction

Uses fast_compatible_mask for efficient compatibility checking.
"""

import numpy as np
import sys
import time

sys.path.insert(0, '/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes')

from helpers.agl18 import agl18_orbits, agl18_compat_graph, agl18_orbit_reps
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask, compatible_mask


def entrypoint() -> np.ndarray:
    t0 = time.time()
    d = 5

    print("Building orbits and compatibility graph...", flush=True)
    orbits = agl18_orbits()
    compat = agl18_compat_graph(d=d)
    orbit_reps = agl18_orbit_reps()

    n_orbits = len(orbits)
    print(f"Graph built in {time.time()-t0:.1f}s.", flush=True)

    # Find the best orbit clique (greedy, degree-ordered from all 720 starting vertices)
    print("Finding best orbit clique...", flush=True)
    best_clique = []
    for sv in range(n_orbits):
        clique = [sv]
        cands = list(np.where(compat[sv])[0])
        while cands:
            scored = [(c, sum(compat[c, c2] for c2 in cands)) for c in cands]
            scored.sort(key=lambda x: -x[1])
            v = scored[0][0]
            clique.append(v)
            cands = [c for c in cands if compat[v, c]]
        if len(clique) > len(best_clique):
            best_clique = clique

    print(f"Best orbit clique: {len(best_clique)} orbits → {len(best_clique)*56} codewords", flush=True)

    # Get all permutations in the orbit clique
    print("Building all permutations and bucket IDs...", flush=True)
    all_perms = build_all_perms()  # shape (40320, 8)

    # Find indices of orbit clique permutations in all_perms
    perm_to_idx = {tuple(p): i for i, p in enumerate(all_perms)}

    orbit_clique_indices = []
    for c in best_clique:
        for p in orbits[c]:
            orbit_clique_indices.append(perm_to_idx[tuple(p)])

    orbit_clique_indices = np.array(sorted(orbit_clique_indices))

    # Precompute bucket IDs for fast compatibility checking
    bucket_ids = build_bucket_ids(all_perms)

    # Find permutations compatible with the orbit clique (NOT in any orbit)
    print("Finding compatible individual permutations...", flush=True)

    # All permutations NOT in the orbit clique
    all_indices = np.arange(len(all_perms))
    non_orbit_mask = ~np.isin(all_indices, orbit_clique_indices)
    non_orbit_indices = all_indices[non_orbit_mask]

    # Use fast compatible mask to find which non-orbit perms are compatible
    compat_mask = fast_compatible_mask(orbit_clique_indices, bucket_ids)

    # Only consider non-orbit permutations
    individual_compat_mask = compat_mask.copy()
    individual_compat_mask[orbit_clique_indices] = False

    compatible_non_orbit = np.where(individual_compat_mask)[0]
    print(f"Found {len(compatible_non_orbit)} individual permutations compatible with the orbit clique", flush=True)

    if len(compatible_non_orbit) == 0:
        # No individual extensions possible, just return orbit clique
        print("No individual extensions possible. Returning pure orbit clique.", flush=True)
        code = all_perms[orbit_clique_indices].astype(np.int32)
        return code

    # Greedily add compatible permutations - use fast bucket-based method
    # Track remaining compatible indices, greedily pick one at a time
    code_indices = list(orbit_clique_indices)
    remaining = list(compatible_non_orbit)
    added_count = 0

    while remaining:
        # Pick the first compatible permutation
        p_idx = remaining.pop(0)
        code_indices.append(p_idx)
        added_count += 1

        if added_count % 10 == 0:
            print(f"Added {added_count} individuals. Remaining: {len(remaining)}", flush=True)

        # Update remaining: keep only those still compatible with new codeword
        # Re-check using fast_compatible_mask with current code
        current_code_indices = np.array(code_indices)
        new_mask = fast_compatible_mask(current_code_indices[-1:], bucket_ids)

        # Filter remaining to only those still compatible
        remaining = [idx for idx in remaining if new_mask[idx]]

    print(f"\nTotal: {len(best_clique)} orbits + {added_count} individuals = {len(code_indices)} codewords", flush=True)
    print(f"Total time: {time.time()-t0:.1f}s", flush=True)

    # Build final code
    code = all_perms[np.array(code_indices)].astype(np.int32)

    print(f"Final code size: {code.shape[0]}", flush=True)
    return code