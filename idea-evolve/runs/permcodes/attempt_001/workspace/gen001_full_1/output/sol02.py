# fitness: TBD
"""
1-for-2 swap search for M(8,5) > 616.

The AGL 616-code is maximal. To beat 616, we need a different structure.
This solution:
1. Finds perms blocked by only 1 codeword ("single-blocker perms")
2. For each such codeword c, checks if any 2 single-blocker perms are mutually compatible
3. If yes: remove c, add the 2 perms → size 617
4. Also tries ILS with various removal fractions

Key insight: two perms p1, p2 are compatible iff they don't share any 4-position bucket.
This is EXACT (not a heuristic) per compat.py documentation.
"""

import numpy as np
import time
from itertools import combinations

from helpers.agl18 import agl18_max_clique_code
from helpers.compat import build_all_perms, build_bucket_ids, fast_compatible_mask


def build_bucket_inv(bucket_ids):
    N, n_subsets = bucket_ids.shape
    bucket_inv = []
    for s in range(n_subsets):
        inv_s = {}
        for i in range(N):
            v = int(bucket_ids[i, s])
            if v not in inv_s:
                inv_s[v] = []
            inv_s[v].append(i)
        bucket_inv.append(inv_s)
    return bucket_inv


def greedy_extend_set(seed_indices, bucket_ids, bucket_inv, N, rng=None):
    """Fast greedy extension using set operations."""
    n_subsets = bucket_ids.shape[1]
    candidates = set(range(N))
    current = []

    for idx in seed_indices:
        if idx not in candidates:
            continue
        current.append(idx)
        candidates.discard(idx)
        for s in range(n_subsets):
            v = int(bucket_ids[idx, s])
            for blocked in bucket_inv[s].get(v, []):
                candidates.discard(blocked)

    cands_list = list(candidates)
    if rng is not None:
        rng.shuffle(cands_list)

    for c in cands_list:
        if c not in candidates:
            continue
        current.append(c)
        candidates.discard(c)
        for s in range(n_subsets):
            v = int(bucket_ids[c, s])
            for blocked in bucket_inv[s].get(v, []):
                candidates.discard(blocked)

    return current


def entrypoint():
    start_time = time.time()
    n, d = 8, 5

    all_perms = build_all_perms(n)
    N = len(all_perms)
    bucket_ids = build_bucket_ids(all_perms, n, d)
    n_subsets = bucket_ids.shape[1]

    perm_to_idx = {}
    for i, p in enumerate(all_perms):
        perm_to_idx[tuple(p.tolist())] = i

    bucket_inv = build_bucket_inv(bucket_ids)
    print(f"Setup done: {time.time()-start_time:.2f}s")

    # AGL 616-code
    agl_code = agl18_max_clique_code(d=d)
    agl_indices = np.array([perm_to_idx[tuple(p.tolist())] for p in agl_code], dtype=np.int32)
    code_set = set(agl_indices.tolist())
    print(f"AGL 616-code ready, t={time.time()-start_time:.2f}s")

    # Build bucket_code_set[s][v] = set of codewords with bucket value v at subset s
    bucket_code_set = []
    for s in range(n_subsets):
        bcs = {}
        for c in code_set:
            v = int(bucket_ids[c, s])
            if v not in bcs:
                bcs[v] = set()
            bcs[v].add(c)
        bucket_code_set.append(bcs)

    # Find single-blocker perms
    single_blocker_perms = {c: [] for c in code_set}
    non_code_perms = [i for i in range(N) if i not in code_set]

    for p in non_code_perms:
        blockers = set()
        for s in range(n_subsets):
            v = int(bucket_ids[p, s])
            if v in bucket_code_set[s]:
                blockers |= bucket_code_set[s][v]
        if len(blockers) == 1:
            c = next(iter(blockers))
            single_blocker_perms[c].append(p)

    print(f"Single-blocker analysis done, t={time.time()-start_time:.2f}s")

    counts = [(c, len(v)) for c, v in single_blocker_perms.items() if v]
    counts.sort(key=lambda x: -x[1])
    print(f"Codewords with single-blocker candidates: {len(counts)}")
    if counts:
        print(f"Candidate counts: {[n for _, n in counts[:10]]}")

    best_code_indices = list(agl_indices)
    best_size = len(best_code_indices)
    TIME_LIMIT = 27

    # Stage 1: 1-for-2 swaps
    print("Trying 1-for-2 swaps...")
    for c, cands in counts:
        if time.time() - start_time > TIME_LIMIT:
            break
        if len(cands) < 2:
            continue

        cands_arr = np.array(cands, dtype=np.int32)
        cands_bids = bucket_ids[cands_arr]  # (n_cands, 70)
        n_cands = len(cands_arr)

        for i in range(n_cands):
            if time.time() - start_time > TIME_LIMIT:
                break
            for j in range(i + 1, n_cands):
                # Compatible iff no shared bucket
                if not np.any(cands_bids[i] == cands_bids[j]):
                    new_code = [x for x in best_code_indices if x != c]
                    new_code.append(int(cands_arr[i]))
                    new_code.append(int(cands_arr[j]))
                    if len(new_code) > best_size:
                        best_size = len(new_code)
                        best_code_indices = new_code
                        print(f"  1-for-2 swap found! Size → {best_size}")
                        # Try to extend further
                        ext = greedy_extend_set(best_code_indices, bucket_ids, bucket_inv, N)
                        if len(ext) > best_size:
                            best_size = len(ext)
                            best_code_indices = ext
                            print(f"  Extended to {best_size}")

    # Stage 2: ILS with various removal fractions
    rng = np.random.RandomState(42)
    attempt = 0
    while time.time() - start_time < TIME_LIMIT:
        frac = 0.05 + (attempt % 20) * 0.04  # 5% to 81%
        frac = min(frac, 0.80)
        k = max(1, int(len(best_code_indices) * frac))
        remove_pos = set(rng.choice(len(best_code_indices), size=k, replace=False).tolist())
        seed = [best_code_indices[i] for i in range(len(best_code_indices)) if i not in remove_pos]

        new_code = greedy_extend_set(seed, bucket_ids, bucket_inv, N, rng=rng)
        if len(new_code) > best_size:
            best_size = len(new_code)
            best_code_indices = new_code
            print(f"  ILS attempt {attempt}: NEW BEST {best_size}, t={time.time()-start_time:.1f}s")
        attempt += 1

    print(f"Final: {best_size} codewords, {attempt} ILS attempts, t={time.time()-start_time:.2f}s")
    return all_perms[np.array(best_code_indices)].astype(np.int32)
