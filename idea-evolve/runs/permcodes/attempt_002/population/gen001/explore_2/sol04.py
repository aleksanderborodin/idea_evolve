# fitness: TBD
"""
Simpler faster ILNS for M(8,5).

Key: start with good greedy, then focus on efficient destroy-repair.
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


def greedy_with_order(order, all_perms, bucket_ids):
    code = [order[0]]
    remaining_mask = np.ones(len(all_perms), dtype=bool)
    remaining_mask[order[0]] = False

    for idx in order[1:]:
        if remaining_mask[idx]:
            code.append(idx)

    return code


def run_one(seed, n_iters=400):
    rng = np.random.RandomState(seed)
    all_perms = ALL_PERMS
    bucket_ids = BUCKET_IDS

    order = rng.permutation(len(all_perms))
    code = greedy_with_order(order, all_perms, bucket_ids)
    best_code = list(code)
    best_size = len(code)

    for it in range(n_iters):
        r = np.random.RandomState(seed + it * 12345)

        k = max(2, len(code) // 4)
        keep_idx = r.choice(len(code), len(code) - k, replace=False)
        keep_set = set(keep_idx)
        surviving = [code[i] for i in range(len(code)) if i in keep_set]

        mask = fast_compatible_mask(np.array(surviving, dtype=np.int32), bucket_ids)
        for s in surviving:
            mask[s] = False
        candidates = np.where(mask)[0]

        r.shuffle(candidates)
        new_code = list(surviving)

        for cand in candidates:
            dists = np.sum(all_perms[cand] != all_perms[new_code], axis=1)
            if np.all(dists >= D):
                new_code.append(cand)

        if len(new_code) >= best_size:
            code = new_code
            if len(code) > best_size:
                best_size = len(code)
                best_code = list(code)

    return best_code, best_size


def entrypoint():
    setup()
    print("Running ILNS...", flush=True)

    np.random.seed(42)
    best_overall = []
    best_size = 0

    for restart in range(25):
        code, size = run_one(seed=42 + restart * 999, n_iters=500)
        if size > best_size:
            best_size = size
            best_overall = code
            print(f"Restart {restart}: new best = {best_size}", flush=True)

    print(f"Final: {best_size} codewords", flush=True)
    return ALL_PERMS[np.array(best_overall, dtype=np.int32)]


if __name__ == "__main__":
    result = entrypoint()
    print(f"Result: {len(result)}")