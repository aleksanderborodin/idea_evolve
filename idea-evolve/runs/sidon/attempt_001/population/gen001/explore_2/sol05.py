# fitness: TBD
"""Exhaustive 2-opt search for Sidon sets.

Key insight from experiments:
1. Greedy ALWAYS gives 66 regardless of element ordering
2. Single-removal + greedy-refill gives NO improvement (greedy 66-set is a strict local optimum under 1-opt)
3. Double-removal + greedy-refill CAN improve (sol04 found 67)

This solution does EXHAUSTIVE 2-opt:
- For every pair of elements in S, remove both and greedy-fill
- If any pair gives net gain >= 1, take the best such pair
- Repeat until no improvement or time runs out
- Then do exhaustive 3-opt (random sampling) for remaining time

Optimization: precompute diff arrays for each element so pair removal is fast.
"""

import time
import numpy as np
import random


def entrypoint():
    N = 10000
    TIME_LIMIT = 26
    start_time = time.time()

    # Build initial greedy set (fast, sequential)
    S_list = []
    ud = np.zeros(N + 2, dtype=bool)

    for c in range(N + 1):
        ok = True
        nd = []
        for s in S_list:
            d = c - s
            if ud[d]:
                ok = False
                break
            nd.append(d)
        if ok:
            S_list.append(c)
            for d in nd:
                ud[d] = True

    best_S = list(S_list)

    def rebuild_ud(S):
        ud = np.zeros(N + 2, dtype=bool)
        for i in range(len(S)):
            for j in range(i + 1, len(S)):
                ud[S[j] - S[i]] = True
        return ud

    def find_addable_mask(S_arr, ud):
        """Numpy: return bool mask of addable elements in {0..N}."""
        if len(S_arr) == 0:
            return np.ones(N + 1, dtype=bool)
        candidates = np.arange(N + 1)
        M = np.abs(candidates[:, None] - S_arr[None, :])  # (N+1, |S|)
        M = np.minimum(M, N + 1)
        blocked = np.any(ud[M], axis=1)
        in_S = np.zeros(N + 1, dtype=bool)
        in_S[S_arr] = True
        return ~blocked & ~in_S

    def greedy_count_from_mask(S_minus, ud_minus, addable_indices):
        """Greedily add elements from addable_indices (sorted) to S_minus."""
        S_cur = list(S_minus)
        ud_cur = ud_minus.copy()
        added = 0
        for c in addable_indices:
            ok = True
            nd = []
            for s in S_cur:
                d = abs(c - s)
                if d > N + 1:
                    continue
                if ud_cur[d]:
                    ok = False
                    break
                nd.append(d)
            if ok:
                S_cur.append(c)
                for d in nd:
                    ud_cur[d] = True
                added += 1
        return added, S_cur

    def do_kopt(S_list, ud, k=2):
        """Try all k-subsets for removal, return best new set."""
        S_arr = np.array(S_list, dtype=np.int32)
        n = len(S_arr)

        # Precompute diff arrays for each element
        diffs_by_elem = []
        for i in range(n):
            xi = S_arr[i]
            d_arr = np.abs(xi - S_arr)
            d_arr = d_arr[d_arr > 0]  # exclude self-diff (0)
            diffs_by_elem.append(d_arr)

        best_gain = 0
        best_new_S = None

        if k == 2:
            total_pairs = n * (n - 1) // 2
            for i in range(n):
                if time.time() - start_time > TIME_LIMIT - 1:
                    break
                for j in range(i + 1, n):
                    # Remove S[i] and S[j]
                    mask_ij = np.ones(n, dtype=bool)
                    mask_ij[i] = False
                    mask_ij[j] = False
                    S_minus = S_arr[mask_ij]

                    # New ud: remove diffs from i and j
                    freed = np.unique(np.concatenate([diffs_by_elem[i], diffs_by_elem[j]]))
                    # But diffs_by_elem[i] includes diff |S[i]-S[j]| and vice versa
                    # We must not double-count. Since each diff appears once in valid Sidon,
                    # just set all freed diffs to False.
                    ud_new = ud.copy()
                    freed_clipped = freed[freed <= N + 1]
                    ud_new[freed_clipped] = False

                    # Find addable candidates
                    addable_mask = find_addable_mask(S_minus, ud_new)
                    addable = np.where(addable_mask)[0]

                    if len(addable) < 3:  # need >=3 to gain from removing 2
                        continue

                    # Greedy fill
                    n_added, new_S = greedy_count_from_mask(
                        S_minus.tolist(), ud_new, addable.tolist()
                    )
                    gain = n_added - 2
                    if gain > best_gain:
                        best_gain = gain
                        best_new_S = new_S

        return best_gain, best_new_S

    def do_kopt_random(S_list, ud, k=3, n_trials=None):
        """Random k-opt sampling."""
        S_arr = np.array(S_list, dtype=np.int32)
        n = len(S_arr)

        diffs_by_elem = []
        for i in range(n):
            xi = S_arr[i]
            d_arr = np.abs(xi - S_arr)
            d_arr = d_arr[d_arr > 0]
            diffs_by_elem.append(d_arr)

        best_gain = 0
        best_new_S = None
        trials = 0

        while time.time() - start_time < TIME_LIMIT - 0.5:
            if n_trials and trials >= n_trials:
                break
            trials += 1

            # Random k indices to remove
            idxs = sorted(random.sample(range(n), k))
            mask = np.ones(n, dtype=bool)
            for idx in idxs:
                mask[idx] = False
            S_minus = S_arr[mask]

            # Freed diffs
            all_freed = np.unique(np.concatenate([diffs_by_elem[idx] for idx in idxs]))
            ud_new = ud.copy()
            ud_new[all_freed[all_freed <= N + 1]] = False

            # Find addable
            addable_mask = find_addable_mask(S_minus, ud_new)
            addable = np.where(addable_mask)[0]

            if len(addable) < k + 1:
                continue

            n_added, new_S = greedy_count_from_mask(
                S_minus.tolist(), ud_new, addable.tolist()
            )
            gain = n_added - k
            if gain > best_gain:
                best_gain = gain
                best_new_S = new_S

        return best_gain, best_new_S

    # Main loop: iterative k-opt
    improved = True
    while improved and time.time() - start_time < TIME_LIMIT - 2:
        improved = False
        S_list = list(best_S)
        ud = rebuild_ud(S_list)

        # Exhaustive 2-opt
        gain, new_S = do_kopt(S_list, ud, k=2)
        if gain > 0 and new_S:
            best_S = sorted(new_S)
            improved = True

    # Random 3-opt for remaining time
    if time.time() - start_time < TIME_LIMIT - 1:
        S_list = list(best_S)
        ud = rebuild_ud(S_list)
        gain, new_S = do_kopt_random(S_list, ud, k=3)
        if gain > 0 and new_S:
            best_S = sorted(new_S)

        # 4-opt if still time
        if time.time() - start_time < TIME_LIMIT - 1:
            S_list = list(best_S)
            ud = rebuild_ud(S_list)
            gain, new_S = do_kopt_random(S_list, ud, k=4)
            if gain > 0 and new_S:
                best_S = sorted(new_S)

    return best_S
