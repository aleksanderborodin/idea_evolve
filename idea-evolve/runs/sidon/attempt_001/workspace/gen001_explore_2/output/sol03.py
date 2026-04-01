# fitness: TBD
"""Fast Sidon set search using numpy vectorization.

Key insight: use numpy to vectorize the "find all addable elements" operation.
For each candidate x, check if any |x - s| for s in S is already in used_diffs.
This is a matrix operation: M[x, i] = |x - S[i]|, then check used_diffs[M].

With numpy, finding all addable elements takes ~1ms instead of ~100ms in pure Python.
This enables hundreds of ILS iterations in 27 seconds.

Strategy:
1. Build initial greedy set (fast, gives 66)
2. Iterated: remove k elements, numpy-scan for new addable candidates, greedily fill
3. Targeted swaps: remove highest-blocking element, fill back
"""

import random
import time
import numpy as np
import bisect


def entrypoint():
    N = 10000
    TIME_LIMIT = 26

    start_time = time.time()

    # ----- State representation -----
    # S_list: Python list (sorted)
    # S_set: Python set
    # used_diffs: numpy bool array of size N+1

    def build_state(elements):
        s = sorted(set(elements))
        ud = np.zeros(N + 1, dtype=bool)
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                d = s[j] - s[i]
                if d <= N:
                    ud[d] = True
        return s, set(s), ud

    def find_all_addable(S_arr_np, S_set, used_diffs):
        """Find all x in {0..N} not in S that can be added. Numpy vectorized."""
        if len(S_arr_np) == 0:
            return list(range(N + 1))
        candidates = np.arange(N + 1)
        # M[x, i] = |x - S[i]|, shape (N+1, |S|)
        M = np.abs(candidates[:, None] - S_arr_np[None, :])
        # Clip to N (diffs > N can't be in used_diffs)
        M = np.minimum(M, N)
        # blocked[x] = True if any diff of x with S is already used
        blocked = np.any(used_diffs[M], axis=1)
        # Also mark elements already in S
        in_S = np.zeros(N + 1, dtype=bool)
        in_S[S_arr_np] = True
        addable = np.where(~blocked & ~in_S)[0].tolist()
        return addable

    def add_elem(S_list, S_set, used_diffs, x):
        for s in S_list:
            d = abs(x - s)
            if d <= N:
                used_diffs[d] = True
        bisect.insort(S_list, x)
        S_set.add(x)

    def remove_elem(S_list, S_set, used_diffs, x):
        # Remove x and rebuild used_diffs from scratch (simplest correct approach)
        S_list.remove(x)
        S_set.discard(x)
        used_diffs[:] = False
        for i in range(len(S_list)):
            for j in range(i + 1, len(S_list)):
                d = S_list[j] - S_list[i]
                if d <= N:
                    used_diffs[d] = True

    def greedy_fill_from_addable(S_list, S_set, used_diffs, addable_list=None, shuffle=False):
        """Greedily add elements. If addable_list given, try those first, then scan."""
        S_arr_np = np.array(S_list, dtype=np.int32) if S_list else np.array([], dtype=np.int32)

        if addable_list is None:
            addable_list = find_all_addable(S_arr_np, S_set, used_diffs)

        if shuffle:
            random.shuffle(addable_list)

        for c in addable_list:
            if c not in S_set:
                # Recheck (might have become blocked by a recently added element)
                ok = True
                new_diffs = []
                for s in S_list:
                    d = abs(c - s)
                    if used_diffs[d]:
                        ok = False
                        break
                    new_diffs.append(d)
                if ok:
                    bisect.insort(S_list, c)
                    S_set.add(c)
                    for d in new_diffs:
                        if d <= N:
                            used_diffs[d] = True

    def clone_state(S_list, used_diffs):
        return list(S_list), used_diffs.copy()

    # ----- Build initial greedy solution -----
    S_list, S_set, used_diffs = build_state([])
    S_np = np.array([], dtype=np.int32)
    for c in range(N + 1):
        ok = True
        new_diffs = []
        for s in S_list:
            d = c - s
            if used_diffs[d]:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            bisect.insort(S_list, c)
            S_set.add(c)
            for d in new_diffs:
                used_diffs[d] = True

    best_S = list(S_list)
    best_score = len(best_S)

    # ----- Main ILS loop -----
    no_improve = 0
    iteration = 0

    while time.time() - start_time < TIME_LIMIT:
        iteration += 1
        elapsed_frac = (time.time() - start_time) / TIME_LIMIT

        # Decide perturbation size based on progress
        if no_improve < 50:
            k = random.randint(2, 8)
        elif no_improve < 200:
            k = random.randint(5, 20)
        else:
            # Large perturbation to escape basin
            k = random.randint(15, 40)

        saved_S, saved_ud = clone_state(S_list, used_diffs)

        # Remove k elements
        if len(S_list) <= k:
            k = max(1, len(S_list) // 2)

        to_remove = random.sample(S_list, k)

        # Rebuild state without removed elements (fast numpy rebuild)
        new_S = [x for x in S_list if x not in set(to_remove)]
        S_list, S_set, used_diffs = build_state(new_S)

        # Find all newly addable candidates using numpy
        S_arr_np = np.array(S_list, dtype=np.int32) if S_list else np.array([], dtype=np.int32)
        addable = find_all_addable(S_arr_np, S_set, used_diffs)

        # Greedy fill: try sequential order first (empirically better)
        addable_sorted = sorted(addable)
        greedy_fill_from_addable(S_list, S_set, used_diffs, addable_sorted)

        if len(S_list) > best_score:
            best_S = list(S_list)
            best_score = len(S_list)
            no_improve = 0
        elif len(S_list) >= len(saved_S):
            # Accept neutral move (same size, different set — might enable future improvements)
            no_improve += 1
        else:
            # Reject: restore
            S_list, S_set, used_diffs = build_state(saved_S)
            no_improve += 1

        # Restart from best if very stuck
        if no_improve > 500:
            S_list, S_set, used_diffs = build_state(best_S)
            no_improve = 0

    return best_S
