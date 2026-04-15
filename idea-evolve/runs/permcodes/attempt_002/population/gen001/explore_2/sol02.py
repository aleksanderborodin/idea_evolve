# fitness: 284
"""
ILNS v2 for M(8,5) — More aggressive search.

Changes from v1:
- More restarts (20 instead of 8)
- More iterations per restart (500 instead of 300)
- Larger destroy fractions (30-50%)
- Tabu-style diversification: avoid recently removed codewords
"""

import numpy as np
from itertools import permutations as iperms
import sys

sys.path.insert(0, '/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes')
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask

N = 8
D = 5
ALL_PERMS = None
BUCKET_IDS = None


def setup():
    global ALL_PERMS, BUCKET_IDS
    if ALL_PERMS is None:
        print("Building permutation index...", flush=True)
        ALL_PERMS = build_all_perms(N)
        BUCKET_IDS = build_bucket_ids(ALL_PERMS)
        print(f"Built {len(ALL_PERMS)} permutations, {BUCKET_IDS.shape[1]} buckets", flush=True)


def greedy_build_random(all_perms, bucket_ids, rng):
    """Greedy construction from random starting point."""
    start_idx = rng.randint(len(all_perms))
    code_indices = [start_idx]

    while True:
        mask = fast_compatible_mask(np.array(code_indices), bucket_ids)
        mask[code_indices] = False
        candidates = np.where(mask)[0]
        if len(candidates) == 0:
            break
        next_idx = candidates[rng.randint(len(candidates))]
        code_indices.append(next_idx)

    return code_indices


def ilns_iterate(code_indices, all_perms, bucket_ids, rng, destroy_frac):
    """Single ILNS destroy-repair iteration."""
    k = max(1, int(len(code_indices) * destroy_frac))
    remove_idx = set(rng.choice(len(code_indices), k, replace=False))
    surviving = [c for i, c in enumerate(code_indices) if i not in remove_idx]

    if len(surviving) == 0:
        return greedy_build_random(all_perms, bucket_ids, rng)

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


def run_aggressive_ilns(seed=42, n_restarts=20, n_iterations=600, verbose=True):
    """Run aggressive ILNS."""
    rng = np.random.RandomState(seed)

    best_overall = []
    best_size = 0
    sizes_history = []

    for restart in range(n_restarts):
        r = np.random.RandomState(seed + restart * 31337)

        code = greedy_build_random(ALL_PERMS, BUCKET_IDS, r)
        greedy_size = len(code)
        sizes_history.append(greedy_size)

        improved_count = 0
        for it in range(n_iterations):
            destroy_frac = 0.3 + 0.2 * r.random()
            new_code = ilns_iterate(code, ALL_PERMS, BUCKET_IDS, r, destroy_frac)

            if len(new_code) >= len(code):
                if len(new_code) > len(code):
                    improved_count += 1
                code = new_code

                if len(code) > best_size:
                    best_size = len(code)
                    best_overall = list(code)
                    if verbose:
                        print(f"R{restart} I{it}: new best = {best_size}", flush=True)

        if verbose and restart % 5 == 0:
            print(f"Restart {restart}/{n_restarts}: greedy={greedy_size}, current={len(code)}, best={best_size}", flush=True)

    if verbose:
        print(f"\nGreedy sizes: min={min(sizes_history)}, max={max(sizes_history)}, avg={np.mean(sizes_history):.1f}")
        print(f"Final best: {best_size} codewords")

    return best_overall


def entrypoint():
    setup()

    print("Running aggressive ILNS v2...", flush=True)

    np.random.seed(42)
    code_indices = run_aggressive_ilns(seed=42, n_restarts=20, n_iterations=600, verbose=True)

    print(f"\nILNS v2 best: {len(code_indices)} codewords", flush=True)

    result = ALL_PERMS[np.array(code_indices)]
    return result


if __name__ == "__main__":
    result = entrypoint()
    print(f"Final code size: {len(result)}")