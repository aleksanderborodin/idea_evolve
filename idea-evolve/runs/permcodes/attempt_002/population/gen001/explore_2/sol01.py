# fitness: 290
"""
Iterated Large Neighborhood Search (ILNS) for M(8,5) permutation codes.

Track B radical exploration: NO algebraic group structure (AGL, etc).
Purely combinatorial/stochastic methods on raw permutation space.

Strategy:
1. Greedy construction from random starting points
2. ILNS: destroy 20-40% of codewords, greedily rebuild
3. Multiple restarts to explore the search space
4. 1-opt intensification on best found code
"""

import numpy as np
from itertools import permutations as iperms
import sys
import os

sys.path.insert(0, '/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes')
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask

N = 8
D = 5
ALL_PERMS = None
BUCKET_IDS = None
PERM_TO_IDX = None


def setup():
    global ALL_PERMS, BUCKET_IDS, PERM_TO_IDX
    if ALL_PERMS is None:
        print("Building permutation index...", flush=True)
        ALL_PERMS = build_all_perms(N)
        BUCKET_IDS = build_bucket_ids(ALL_PERMS)
        PERM_TO_IDX = {tuple(p.tolist()): i for i, p in enumerate(ALL_PERMS)}
        print(f"Built {len(ALL_PERMS)} permutations, {BUCKET_IDS.shape[1]} buckets", flush=True)


def greedy_build(start_idx, all_perms, bucket_ids, rng=None):
    """Greedy construction starting from a given permutation index."""
    if rng is None:
        rng = np.random.RandomState()

    code_indices = [start_idx]
    N = len(all_perms)
    remaining = np.ones(N, dtype=bool)
    remaining[start_idx] = False

    while True:
        mask = fast_compatible_mask(np.array(code_indices), bucket_ids)
        mask[code_indices] = False
        candidates = np.where(mask)[0]
        if len(candidates) == 0:
            break
        next_idx = candidates[rng.randint(len(candidates))]
        code_indices.append(next_idx)

    return code_indices


def ilns_destroy_repair(code_indices, all_perms, bucket_ids, rng, destroy_frac=0.3):
    """Destroy a fraction of codewords and greedily rebuild."""
    k = max(1, int(len(code_indices) * destroy_frac))
    remove_indices = set(rng.choice(len(code_indices), k, replace=False))
    surviving = [c for i, c in enumerate(code_indices) if i not in remove_indices]

    if len(surviving) == 0:
        return greedy_build(rng.randint(len(all_perms)), all_perms, bucket_ids, rng)

    mask = fast_compatible_mask(np.array(surviving), bucket_ids)
    for s in surviving:
        mask[s] = False
    candidates = np.where(mask)[0]

    if len(candidates) == 0:
        return surviving

    rng.shuffle(candidates)
    new_code = list(surviving)

    for cand in candidates:
        dists = np.sum(all_perms[cand] != all_perms[new_code], axis=1)
        if np.all(dists >= D):
            new_code.append(cand)

    return new_code


def one_opt_improve(code_indices, all_perms, bucket_ids, rng):
    """Try to improve each codeword with 2-for-1 swaps."""
    improved = True
    iteration = 0
    best_code = list(code_indices)

    while improved and iteration < 10:
        improved = False
        iteration += 1
        mask = fast_compatible_mask(np.array(best_code), bucket_ids)

        for i in range(len(best_code)):
            if improved:
                break
            old_idx = best_code[i]

            mask_i = mask.copy()
            mask_i[best_code] = False
            candidates = np.where(mask_i)[0]

            if len(candidates) < 2:
                continue

            rng.shuffle(candidates)
            for c1, c2 in zip(candidates[:-1], candidates[1:]):
                dists1 = np.sum(all_perms[c1] != all_perms[best_code], axis=1)
                dists1[i] = 0
                dists2 = np.sum(all_perms[c2] != all_perms[best_code], axis=1)
                dists2[i] = 0

                if np.all(dists1 >= D) and np.all(dists2 >= D):
                    new_code = list(best_code)
                    new_code[i] = c1
                    new_code.append(c2)
                    best_code = new_code
                    improved = True
                    break

    return best_code


def run_ilns(seed=42, n_iterations=300, n_restarts=8, verbose=True):
    """Run ILNS with multiple restarts."""
    rng = np.random.RandomState(seed)

    best_overall = []
    best_overall_size = 0

    for restart in range(n_restarts):
        r = np.random.RandomState(seed + restart * 1000)

        start_idx = r.randint(len(ALL_PERMS))
        code = greedy_build(start_idx, ALL_PERMS, BUCKET_IDS, r)

        if verbose:
            print(f"Restart {restart}: greedy size = {len(code)}", flush=True)

        for it in range(n_iterations):
            destroy_frac = 0.2 + 0.2 * r.random()
            new_code = ilns_destroy_repair(code, ALL_PERMS, BUCKET_IDS, r, destroy_frac)

            if len(new_code) > len(code):
                code = new_code
                if verbose and it % 50 == 0:
                    print(f"  Iter {it}: improved to {len(code)}", flush=True)

        if len(code) > best_overall_size:
            best_overall_size = len(code)
            best_overall = code
            if verbose:
                print(f"*** New best: {len(code)} at restart {restart} ***", flush=True)

    return best_overall


def entrypoint():
    setup()

    print("Running ILNS search...", flush=True)

    np.random.seed(42)
    code_indices = run_ilns(seed=42, n_iterations=300, n_restarts=8, verbose=True)

    print(f"ILNS best: {len(code_indices)} codewords", flush=True)

    print("Running 1-opt intensification...", flush=True)
    rng = np.random.RandomState(999)
    final_code = one_opt_improve(code_indices, ALL_PERMS, BUCKET_IDS, rng)
    print(f"After 1-opt: {len(final_code)} codewords", flush=True)

    result = ALL_PERMS[np.array(final_code)]
    return result


if __name__ == "__main__":
    result = entrypoint()
    print(f"Final code size: {len(result)}")