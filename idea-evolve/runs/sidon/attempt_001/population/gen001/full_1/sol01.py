# fitness: TBD
"""
Iterated local search for Sidon sets.

Start from greedy-66 then apply "remove 1, add 2+" local search moves.
Uses reference-counted diffs for O(k) incremental updates and vectorized
available-candidate computation.
"""
import time
import random
import numpy as np


N = 10000


def _greedy_forward():
    """Standard greedy: add smallest valid element. Returns (S_list, diff_counts)."""
    diff_counts = np.zeros(N + 1, dtype=np.int32)
    S = []
    for c in range(N + 1):
        # Check if addable
        blocked = False
        nd = []
        for s in S:
            d = c - s  # c > s always (forward scan), so d > 0
            if diff_counts[d] > 0 or d in nd:
                blocked = True
                break
            nd.append(d)
        if not blocked:
            S.append(c)
            for d in nd:
                diff_counts[d] += 1
    return S, diff_counts


def _find_available(S_arr, diff_counts):
    """Vectorized: find all candidates not blocked by current diff_counts."""
    blocked = np.zeros(N + 1, dtype=bool)
    blocked[S_arr] = True
    used_d = np.where(diff_counts > 0)[0]
    if len(used_d) == 0:
        pass
    else:
        for s in S_arr:
            pos = s + used_d
            neg = s - used_d
            blocked[pos[(pos >= 0) & (pos <= N)]] = True
            blocked[neg[(neg >= 0) & (neg <= N)]] = True
    return np.where(~blocked)[0]


def _can_add(c, S_arr, diff_counts):
    """Check if c can be added. Returns (ok, new_diffs_array)."""
    nd = np.abs(S_arr - c)
    if len(nd) == 0:
        return True, nd
    # Check uniqueness of new diffs (no two elements equidistant from c)
    nd_sorted = np.sort(nd)
    if np.any(nd_sorted[1:] == nd_sorted[:-1]):
        return False, nd
    # Check no conflict with existing diffs
    if np.any(diff_counts[nd] > 0):
        return False, nd
    return True, nd


def _local_search(S_init, diff_counts_init, deadline):
    """Remove-1/add-2+ local search. Returns improved (S, diff_counts)."""
    S = list(S_init)
    diff_counts = diff_counts_init.copy()
    best = list(S)

    improved = True
    while improved and time.time() < deadline:
        improved = False
        random.shuffle(S)  # vary removal order to escape ordering bias

        for idx in range(len(S)):
            if time.time() > deadline:
                break

            elem = S[idx]
            S_new = S[:idx] + S[idx + 1:]
            S_new_arr = np.array(S_new, dtype=np.int32)

            # Decrement diffs involving elem
            dc = diff_counts.copy()
            for s in S_new:
                dc[abs(elem - s)] -= 1

            # Find available candidates (not blocked)
            avail = _find_available(S_new_arr, dc)
            if len(avail) < 2:
                continue

            # Greedily add from available
            added = []
            cur_S_arr = S_new_arr.copy()
            cur_dc = dc.copy()

            for c in avail:
                ok, nd = _can_add(c, cur_S_arr, cur_dc)
                if ok:
                    added.append(c)
                    cur_dc[nd] += 1
                    cur_S_arr = np.append(cur_S_arr, c)
                    if len(added) >= 2:
                        break

            if len(added) >= 2:
                S = sorted(S_new + added)
                # Rebuild diff_counts
                diff_counts = np.zeros(N + 1, dtype=np.int32)
                S_arr_full = np.array(S, dtype=np.int32)
                for i in range(len(S_arr_full)):
                    nd = np.abs(S_arr_full[:i] - S_arr_full[i])
                    diff_counts[nd] += 1
                if len(S) > len(best):
                    best = list(S)
                improved = True
                break

    return best, diff_counts


def _iterated_local_search(S_init, diff_counts_init, deadline):
    """ILS: perturbation + local search loop."""
    best_S = list(S_init)
    best_dc = diff_counts_init.copy()
    current_S = list(S_init)
    current_dc = diff_counts_init.copy()

    while time.time() < deadline:
        # Perturbation: remove k random elements, then greedily fill
        k = random.randint(2, 5)
        to_remove = random.sample(current_S, min(k, len(current_S)))

        S_perturbed = [x for x in current_S if x not in set(to_remove)]
        dc_perturbed = np.zeros(N + 1, dtype=np.int32)
        arr_p = np.array(S_perturbed, dtype=np.int32)
        for i in range(len(arr_p)):
            nd = np.abs(arr_p[:i] - arr_p[i])
            dc_perturbed[nd] += 1

        # Greedy fill after perturbation
        S_arr = np.array(sorted(S_perturbed), dtype=np.int32)
        dc_f = dc_perturbed.copy()
        S_list = sorted(S_perturbed)
        for c in range(N + 1):
            if c in set(S_list):
                continue
            ok, nd = _can_add(c, S_arr, dc_f)
            if ok:
                S_list.append(c)
                S_arr = np.append(S_arr, c)
                dc_f[nd] += 1

        # Local search on perturbed+filled
        if time.time() < deadline - 1:
            sub_deadline = min(deadline, time.time() + 5)
            S_ls, dc_ls = _local_search(S_list, dc_f, sub_deadline)
        else:
            S_ls, dc_ls = S_list, dc_f

        if len(S_ls) > len(best_S):
            best_S = list(S_ls)
            best_dc = dc_ls.copy()
            current_S = list(S_ls)
            current_dc = dc_ls.copy()

    return best_S


def entrypoint():
    start = time.time()
    DEADLINE = start + 27

    # Build greedy baseline
    S_greedy, dc_greedy = _greedy_forward()

    # Initial local search on greedy result
    ls_deadline = min(DEADLINE - 5, start + 15)
    S_ls, dc_ls = _local_search(S_greedy, dc_greedy, ls_deadline)

    # ILS for remaining time
    best = _iterated_local_search(S_ls, dc_ls, DEADLINE - 0.5)

    if len(S_ls) > len(best):
        best = S_ls

    return sorted(best)
