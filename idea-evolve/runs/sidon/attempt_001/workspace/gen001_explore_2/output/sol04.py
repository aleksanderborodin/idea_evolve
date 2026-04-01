# fitness: TBD
"""Targeted removal search for Sidon sets.

Key insight: in a maximal Sidon set (no element can be added), we need to REMOVE
some elements to make room. The question is: which elements to remove, and which
to add back.

For a VALID Sidon set, each diff appears exactly ONCE. So removing element x
frees exactly {|x - t| : t in S, t != x} diffs.

This means: after removing x, we can precisely compute which candidates become addable.
If removing x allows us to add 2+ elements (net gain >= 1), we take that move.

Search strategy:
1. For each element x in S, compute candidates_after_remove_x using numpy
2. Greedy fill to count how many we can add from those candidates
3. If any x gives net gain, take the best one
4. Repeat until no improvement or time runs out
"""

import time
import numpy as np
import bisect
import random


def entrypoint():
    N = 10000
    TIME_LIMIT = 26
    start_time = time.time()

    # ----- Build initial greedy set -----
    S_list = []
    used_diffs = np.zeros(N + 2, dtype=bool)

    for c in range(N + 1):
        diffs_new = []
        ok = True
        for s in S_list:
            d = c - s  # c > s since we go in order
            if used_diffs[d]:
                ok = False
                break
            diffs_new.append(d)
        if ok:
            S_list.append(c)
            for d in diffs_new:
                used_diffs[d] = True

    best_S = list(S_list)
    best_score = len(best_S)

    def rebuild_used_diffs(S):
        ud = np.zeros(N + 2, dtype=bool)
        for i in range(len(S)):
            for j in range(i + 1, len(S)):
                d = S[j] - S[i]
                ud[d] = True
        return ud

    def find_addable_after_remove(S_arr, used_diffs, x_idx):
        """Find all candidates addable to S after removing S[x_idx]."""
        x = S_arr[x_idx]
        S_minus = np.concatenate([S_arr[:x_idx], S_arr[x_idx + 1:]])

        # New used_diffs: remove all diffs involving x
        freed = np.abs(x - S_minus)
        new_ud = used_diffs.copy()
        new_ud[freed] = False  # Valid for Sidon: each diff appears once

        # Find all z in {0..N} not in S that can be added to S\{x}
        n_minus = len(S_minus)
        if n_minus == 0:
            return new_ud, S_minus, np.arange(N + 1)

        candidates = np.arange(N + 1)
        # M[z, j] = |z - S_minus[j]|, shape (N+1, n-1)
        M = np.abs(candidates[:, None] - S_minus[None, :])
        M = np.minimum(M, N + 1)
        # Pad new_ud to avoid index errors
        new_ud_padded = np.zeros(N + 2, dtype=bool)
        new_ud_padded[:len(new_ud)] = new_ud
        blocked = np.any(new_ud_padded[M], axis=1)
        in_S = np.zeros(N + 1, dtype=bool)
        in_S[S_arr] = True
        addable = np.where(~blocked & ~in_S)[0]
        return new_ud, S_minus, addable

    def greedy_count(S_minus_list, new_ud, addable_sorted):
        """Count how many elements we can add from addable_sorted to S_minus."""
        current = list(S_minus_list)
        ud = new_ud.copy()
        added = 0
        for c in addable_sorted:
            ok = True
            new_diffs = []
            for s in current:
                d = abs(c - s)
                if d > N + 1:
                    continue
                if ud[d]:
                    ok = False
                    break
                new_diffs.append(d)
            if ok:
                bisect.insort(current, c)
                for d in new_diffs:
                    ud[d] = True
                added += 1
        return added, current

    # ----- Targeted removal search -----
    improved = True
    while improved and time.time() - start_time < TIME_LIMIT:
        improved = False
        S_arr = np.array(S_list, dtype=np.int32)
        used_diffs = rebuild_used_diffs(S_list)

        best_gain = 0
        best_new_S = None

        # Try removing each element
        for i in range(len(S_arr)):
            if time.time() - start_time > TIME_LIMIT - 1:
                break

            new_ud, S_minus_arr, addable = find_addable_after_remove(S_arr, used_diffs, i)

            if len(addable) == 0:
                continue

            # Greedy fill (sequential order - empirically better)
            addable_sorted = sorted(addable.tolist())
            n_added, new_S = greedy_count(S_minus_arr.tolist(), new_ud, addable_sorted)

            gain = n_added - 1  # removed 1, added n_added
            if gain > best_gain:
                best_gain = gain
                best_new_S = new_S

        if best_new_S is not None and best_gain > 0:
            S_list = sorted(best_new_S)
            if len(S_list) > best_score:
                best_S = list(S_list)
                best_score = len(S_list)
            improved = True
            used_diffs = rebuild_used_diffs(S_list)

    # ----- If no single-removal improvement, try double removal -----
    # (brute force all pairs - may not complete in time)
    if time.time() - start_time < TIME_LIMIT - 5:
        S_arr = np.array(S_list, dtype=np.int32)
        used_diffs = rebuild_used_diffs(S_list)
        n = len(S_arr)

        # Try random pairs
        pairs_tried = 0
        while time.time() - start_time < TIME_LIMIT - 2:
            i, j = random.sample(range(n), 2)
            if i > j:
                i, j = j, i
            xi, xj = S_arr[i], S_arr[j]

            # Remove both
            S_minus = [s for k, s in enumerate(S_arr.tolist()) if k != i and k != j]
            new_ud = rebuild_used_diffs(S_minus)

            if not S_minus:
                continue

            S_minus_arr = np.array(S_minus, dtype=np.int32)
            candidates = np.arange(N + 1)
            M = np.abs(candidates[:, None] - S_minus_arr[None, :])
            M = np.minimum(M, N + 1)
            new_ud_padded = np.zeros(N + 2, dtype=bool)
            new_ud_padded[:len(new_ud)] = new_ud
            blocked = np.any(new_ud_padded[M], axis=1)
            in_S = np.zeros(N + 1, dtype=bool)
            in_S[S_arr] = True
            addable = np.where(~blocked & ~in_S)[0]

            addable_sorted = sorted(addable.tolist())
            n_added, new_S = greedy_count(S_minus, new_ud, addable_sorted)

            gain = n_added - 2  # removed 2
            if gain > 0 and len(new_S) > best_score:
                S_list = sorted(new_S)
                best_S = list(S_list)
                best_score = len(best_S)
                S_arr = np.array(S_list, dtype=np.int32)
                used_diffs = rebuild_used_diffs(S_list)
                n = len(S_arr)

            pairs_tried += 1

    return best_S
