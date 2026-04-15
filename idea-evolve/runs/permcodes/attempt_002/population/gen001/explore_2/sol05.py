# fitness: 293
"""
ILNS v3 for M(8,5) - Fixed greedy + destroy/repair.

Key insight: need to properly check compatibility at each step.
"""

import numpy as np
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
        print("Building...", flush=True)
        ALL_PERMS = build_all_perms(N)
        BUCKET_IDS = build_bucket_ids(ALL_PERMS)
        print(f"Done: {len(ALL_PERMS)} perms", flush=True)


def greedy_build(start_idx, all_perms, bucket_ids, rng):
    code = [start_idx]
    while True:
        mask = fast_compatible_mask(np.array(code, dtype=np.int32), bucket_ids)
        mask[code] = False
        candidates = np.where(mask)[0]
        if len(candidates) == 0:
            break
        code.append(candidates[rng.randint(len(candidates))])
    return code


def ilns_iterate(code, all_perms, bucket_ids, rng, destroy_frac):
    k = max(1, int(len(code) * destroy_frac))
    remove_set = set(rng.choice(len(code), k, replace=False))
    surviving = [c for i, c in enumerate(code) if i not in remove_set]

    if len(surviving) == 0:
        return greedy_build(rng.randint(len(all_perms)), all_perms, bucket_ids, rng)

    mask = fast_compatible_mask(np.array(surviving, dtype=np.int32), bucket_ids)
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


def run(seed, n_restarts=15, n_iters=400):
    rng = np.random.RandomState(seed)
    best_code = []
    best_size = 0

    for restart in range(n_restarts):
        r = np.random.RandomState(seed + restart * 7919)

        code = greedy_build(r.randint(len(ALL_PERMS)), ALL_PERMS, BUCKET_IDS, r)
        greedy_size = len(code)

        for it in range(n_iters):
            destroy_frac = 0.2 + 0.25 * r.random()
            new_code = ilns_iterate(code, ALL_PERMS, BUCKET_IDS, r, destroy_frac)

            if len(new_code) >= len(code):
                if len(new_code) > len(code):
                    code = new_code
                else:
                    code = new_code if r.random() < 0.3 else code

                if len(code) > best_size:
                    best_size = len(code)
                    best_code = list(code)
                    print(f"R{restart} I{it}: new best = {best_size}", flush=True)

        if restart % 3 == 0:
            print(f"Restart {restart}: greedy={greedy_size}, best={best_size}", flush=True)

    return best_code, best_size


def entrypoint():
    setup()
    print("Running ILNS v3...", flush=True)

    np.random.seed(42)
    code, size = run(seed=42, n_restarts=15, n_iters=400)

    print(f"\nFinal: {size} codewords", flush=True)
    return ALL_PERMS[np.array(code, dtype=np.int32)]


if __name__ == "__main__":
    result = entrypoint()
    print(f"Result: {len(result)}")