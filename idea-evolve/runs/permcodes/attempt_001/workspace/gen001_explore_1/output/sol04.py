# fitness: TBD
"""
Multiple AGL 11-cliques: check if different 11-clique choices give extensible codes.

The greedy algorithm finds ONE of possibly many 11-cliques in the AGL orbit graph.
Different cliques may give structurally different 616-codes. The one from agl18_max_clique_code()
is maximal (0 extensible perms). But another 11-clique might leave room to add perms.

Strategy:
1. Find ALL 11-cliques in the orbit graph (or a representative sample)
2. For each, build the 616-code
3. Check how many additional perms are compatible with each code
4. For the best, greedily extend

If even one 11-clique yields a code that can be extended by even 1 permutation,
we get 617 — beating the known lower bound.
"""

import numpy as np
from helpers.agl18 import agl18_orbits, agl18_compat_graph
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask
from itertools import permutations as iperms


def find_all_cliques_of_size_k(compat, k, max_cliques=100):
    """Find up to max_cliques cliques of size k using backtracking."""
    n = len(compat)
    cliques = []
    
    def backtrack(clique, cands):
        if len(clique) == k:
            cliques.append(list(clique))
            return
        if len(clique) + len(cands) < k:
            return
        if len(cliques) >= max_cliques:
            return
        for i, v in enumerate(cands):
            new_cands = [c for c in cands[i+1:] if compat[v, c]]
            backtrack(clique + [v], new_cands)
            if len(cliques) >= max_cliques:
                return
    
    order = list(np.argsort(-compat.sum(axis=1)))
    backtrack([], order)
    return cliques


def entrypoint():
    print("Building AGL orbit data...")
    all_perms_arr = np.array(list(iperms(range(8))), dtype=np.int8)
    orbits = agl18_orbits(all_perms_arr)
    compat = agl18_compat_graph(all_perms_arr, d=5)
    n_orbits = len(orbits)
    print(f"  {n_orbits} orbits")

    print("Finding 11-cliques via backtracking (up to 50)...")
    cliques_11 = find_all_cliques_of_size_k(compat, 11, max_cliques=50)
    print(f"  Found {len(cliques_11)} distinct 11-cliques")

    # Build fast compat data
    all_perms_arr_int = np.array(list(iperms(range(8))), dtype=np.int8)
    bucket_ids = build_bucket_ids(all_perms_arr_int, n=8, d=5)
    perm_to_idx = {tuple(p.tolist()): i for i, p in enumerate(all_perms_arr_int)}

    best_code = None
    best_extensions = 0
    
    for ci, clique in enumerate(cliques_11):
        # Build 616-code for this clique
        parts = [orbits[c] for c in clique]
        code_616 = np.vstack(parts).astype(np.int8)
        
        # Check compatibility
        code_idx = np.array([perm_to_idx[tuple(r.tolist())] for r in code_616], dtype=np.int32)
        compat_mask = fast_compatible_mask(code_idx, bucket_ids)
        n_ext = int(compat_mask.sum())
        
        if n_ext > best_extensions:
            best_extensions = n_ext
            best_code = (code_616.copy(), code_idx.copy(), clique)
            print(f"  Clique {ci}: {n_ext} extensible perms")

    print(f"\nBest: {best_extensions} compatible perms for some 616-code")

    if best_extensions == 0:
        # All 11-cliques produce maximal codes — return AGL 616
        print("All 11-cliques are maximal. Returning AGL 616.")
        code_616, _, _ = best_code
        return code_616.astype(np.int32)

    # Extend the best code greedily
    code_616, code_idx, clique = best_code
    compat_mask = fast_compatible_mask(code_idx, bucket_ids)
    compat_idx = list(np.where(compat_mask)[0])
    
    code_indices = list(code_idx)
    added = 0
    while compat_idx:
        chosen = compat_idx[0]
        code_indices.append(chosen)
        new_mask = fast_compatible_mask(np.array([chosen], dtype=np.int32), bucket_ids)
        compat_idx = [idx for idx in compat_idx[1:] if new_mask[idx]]
        added += 1

    print(f"Extended: {len(code_indices)} codewords (+{added})")
    extended = all_perms_arr_int[np.array(code_indices)].astype(np.int32)
    return extended
