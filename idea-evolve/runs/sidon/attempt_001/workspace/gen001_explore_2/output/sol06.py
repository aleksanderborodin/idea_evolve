# fitness: TBD
"""Fixed exhaustive 2-opt + iterative improvement for Sidon sets.

Bug fix from sol05: when doing k-opt (remove k elements, add back),
the greedy would simply RE-ADD the removed elements, giving net gain=0.
Fix: try greedy fill excluding the removed elements. Only count TRULY NEW elements.

A 2-opt gives net gain if: after removing S[i] and S[j], we can find 3+ NEW elements
(not S[i] or S[j]) that can be added to S_minus = S \ {S[i], S[j]}.
Net gain = n_new - 2 (removed 2, kept 0 from removed, added n_new new).

Also try: add removed elements LAST so new elements get priority.
"""

import time
import numpy as np
import random


def entrypoint():
    N = 10000
    TIME_LIMIT = 26
    start_time = time.time()

    # Build initial greedy set
    S_list = []
    for c in range(N + 1):
        ok = True
        nd = []
        for s in S_list:
            d = c - s
            if d in set():  # will be replaced
                ok = False
                break
            nd.append(d)

    # Better greedy with bool array
    ud0 = np.zeros(N + 2, dtype=bool)
    S_list = []
    for c in range(N + 1):
        ok = True
        nd = []
        for s in S_list:
            d = c - s
            if ud0[d]:
                ok = False
                break
            nd.append(d)
        if ok:
            S_list.append(c)
            for d in nd:
                ud0[d] = True

    best_S = list(S_list)

    def rebuild_ud(S):
        ud = np.zeros(N + 2, dtype=bool)
        for i in range(len(S)):
            for j in range(i + 1, len(S)):
                ud[S[j] - S[i]] = True
        return ud

    def find_addable_numpy(S_minus_arr, ud, exclude_set=None):
        """Find candidates addable to S_minus, optionally excluding some elements."""
        if len(S_minus_arr) == 0:
            candidates = np.arange(N + 1)
            mask = np.ones(N + 1, dtype=bool)
            if exclude_set:
                for x in exclude_set:
                    if 0 <= x <= N:
                        mask[x] = False
            return np.where(mask)[0]

        candidates = np.arange(N + 1)
        # M[z, j] = |z - S_minus[j]|
        M = np.abs(candidates[:, None] - S_minus_arr[None, :])
        M = np.minimum(M, N + 1)
        blocked = np.any(ud[M], axis=1)

        in_S_minus = np.zeros(N + 1, dtype=bool)
        in_S_minus[S_minus_arr] = True

        addable_mask = ~blocked & ~in_S_minus

        if exclude_set:
            for x in exclude_set:
                if 0 <= x <= N:
                    addable_mask[x] = False

        return np.where(addable_mask)[0]

    def greedy_from_addable(S_minus, ud, addable_sorted):
        """Sequential greedy from addable list. Returns (n_added, new_S)."""
        cur = list(S_minus)
        ud_cur = ud.copy()
        added = 0
        for c in addable_sorted:
            ok = True
            nd = []
            for s in cur:
                d = abs(c - s)
                if d <= N + 1 and ud_cur[d]:
                    ok = False
                    break
                if d <= N + 1:
                    nd.append(d)
            if ok:
                cur.append(c)
                for d in nd:
                    ud_cur[d] = True
                added += 1
        return added, cur

    def exhaustive_2opt(S_list, ud):
        """Try all pairs. For each, try greedy fill excluding removed elements."""
        S_arr = np.array(S_list, dtype=np.int32)
        n = len(S_arr)

        # Precompute diffs for each element
        diffs_of = []
        for i in range(n):
            xi = S_arr[i]
            d = np.abs(xi - S_arr)
            d = d[d > 0]
            diffs_of.append(d)

        best_gain = 0
        best_new_S = None

        for i in range(n):
            if time.time() - start_time > TIME_LIMIT - 2:
                break
            for j in range(i + 1, n):
                xi, xj = S_arr[i], S_arr[j]

                # Remove i and j
                mask = np.ones(n, dtype=bool)
                mask[i] = False
                mask[j] = False
                S_minus = S_arr[mask]

                # New ud: free diffs of xi and xj
                freed = np.unique(np.concatenate([diffs_of[i], diffs_of[j]]))
                ud_new = ud.copy()
                freed_valid = freed[freed <= N + 1]
                ud_new[freed_valid] = False

                # Find addable EXCLUDING xi and xj (find truly new elements)
                exclude = {int(xi), int(xj)}
                addable_new = find_addable_numpy(S_minus, ud_new, exclude_set=exclude)

                if len(addable_new) < 3:
                    # Can't net gain with just new elements (need 3 to get gain >= 1)
                    # Try with removed elements included but at the end
                    addable_all = find_addable_numpy(S_minus, ud_new)
                    if len(addable_all) < 3:
                        continue
                    # Put new elements first, removed elements last
                    addable_first = [x for x in addable_all.tolist()
                                     if x != xi and x != xj]
                    addable_last = [x for x in [xi, xj]
                                    if x in set(addable_all.tolist())]
                    addable_ordered = sorted(addable_first) + addable_last
                    n_added, new_S = greedy_from_addable(
                        S_minus.tolist(), ud_new, addable_ordered
                    )
                    gain = n_added - 2
                    if gain > best_gain:
                        best_gain = gain
                        best_new_S = new_S
                else:
                    # Try purely new elements first
                    n_added, new_S = greedy_from_addable(
                        S_minus.tolist(), ud_new, sorted(addable_new.tolist())
                    )
                    gain = n_added - 2  # removed 2, added n_added new ones

                    if gain > best_gain:
                        best_gain = gain
                        best_new_S = new_S

        return best_gain, best_new_S

    def random_kopt(S_list, ud, k, n_trials=1000):
        """Random k-opt: remove k, add new elements."""
        S_arr = np.array(S_list, dtype=np.int32)
        n = len(S_arr)

        diffs_of = []
        for i in range(n):
            xi = S_arr[i]
            d = np.abs(xi - S_arr)
            d = d[d > 0]
            diffs_of.append(d)

        best_gain = 0
        best_new_S = None
        trials = 0

        while time.time() - start_time < TIME_LIMIT - 1 and trials < n_trials:
            trials += 1
            idxs = sorted(random.sample(range(n), k))
            removed_vals = {int(S_arr[idx]) for idx in idxs}

            mask = np.ones(n, dtype=bool)
            for idx in idxs:
                mask[idx] = False
            S_minus = S_arr[mask]

            freed = np.unique(np.concatenate([diffs_of[idx] for idx in idxs]))
            ud_new = ud.copy()
            freed_valid = freed[freed <= N + 1]
            ud_new[freed_valid] = False

            # Try with excluded removed elements
            addable = find_addable_numpy(S_minus, ud_new, exclude_set=removed_vals)

            if len(addable) < k + 1:
                continue

            n_added, new_S = greedy_from_addable(
                S_minus.tolist(), ud_new, sorted(addable.tolist())
            )
            gain = n_added - k
            if gain > best_gain:
                best_gain = gain
                best_new_S = new_S

        return best_gain, best_new_S

    # Main iterative improvement
    improved = True
    while improved and time.time() - start_time < TIME_LIMIT - 3:
        improved = False
        ud = rebuild_ud(best_S)

        gain, new_S = exhaustive_2opt(best_S, ud)
        if gain > 0 and new_S:
            best_S = sorted(new_S)
            improved = True

    # Random 3-opt, 4-opt for remaining time
    for k in [3, 4, 5]:
        if time.time() - start_time >= TIME_LIMIT - 1:
            break
        ud = rebuild_ud(best_S)
        gain, new_S = random_kopt(best_S, ud, k=k)
        if gain > 0 and new_S:
            best_S = sorted(new_S)

    return best_S
