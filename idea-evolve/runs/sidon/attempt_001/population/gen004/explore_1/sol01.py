# fitness: TBD
"""
Min-Blocking Greedy for Sidon sets.

At each greedy step, among all valid candidates (those that don't violate the Sidon
property), pick the one with the LOWEST blocking score — i.e., the one that would
block the fewest other currently-valid candidates if added.

Blocking score of candidate c = count of valid c' that would become invalid after adding c.
c' is blocked by adding c if:
  (A) |c' - c| in used_diffs  (c and c' create a diff already used)
  (B) |c' - c| in new_diffs_c = {|c - s| : s in S}  (same new diff for c-c' and c-S)
  (C) exists s in S: |c' - s| in new_diffs_c  (diff of c' with S clashes with diff of c with S)
  [Note: new_blocking[c] = Σ_{s in S} valid[2c - s] computes (B)+(C) combined]

Fast computation using numpy array shifts instead of O(M^2) loops.
"""
import numpy as np


def entrypoint(N=10000):
    valid_arr = np.ones(N + 1, dtype=np.int8)   # valid_arr[c] = 1 if c is valid candidate
    used_diffs_arr = np.zeros(N + 1, dtype=np.int8)  # used_diffs_arr[d] = 1 if d used
    S_indicator = np.zeros(N + 1, dtype=np.int8)  # S_indicator[s] = 1 if s in S
    S = []

    while True:
        valid_indices = np.nonzero(valid_arr)[0]
        if len(valid_indices) == 0:
            break

        if len(S) == 0:
            chosen = int(valid_indices[0])
        else:
            blocking = _compute_blocking(valid_arr, used_diffs_arr, S_indicator, S, N)
            valid_blocking = blocking[valid_indices]
            min_b = valid_blocking.min()
            chosen = int(valid_indices[np.argmax(valid_blocking == min_b)])

        # Add chosen to S
        in_s_arr = np.array(S, dtype=np.int32)
        S.append(chosen)
        S_indicator[chosen] = 1

        # Compute new diffs and mark new blocked candidates
        if len(S) >= 2:
            new_d = np.abs(in_s_arr - chosen)
            new_d = new_d[new_d <= N]
            used_diffs_arr[new_d] = 1

            # Mark newly blocked candidates as invalid
            # c is blocked if |c - chosen| in used_diffs_arr (after update)
            # This check uses the cumulative used_diffs_arr
            _invalidate_blocked(valid_arr, used_diffs_arr, chosen, S, N)

    return S


def _invalidate_blocked(valid_arr, used_diffs_arr, chosen, S, N):
    """Remove candidates that are now invalid after adding 'chosen' to S."""
    # A candidate c is now invalid if any |c - s| for s in S is in used_diffs_arr
    # We only need to check candidates that might have become invalid due to new diffs
    # from 'chosen'. Those are candidates c where |c - s| = |chosen - s'| for some s' in S.
    # Instead, just re-validate all remaining valid candidates against chosen.

    remaining = np.nonzero(valid_arr)[0]
    if len(remaining) == 0:
        return

    # For each remaining valid candidate c, check if |c - chosen| is in used_diffs_arr
    diffs_to_chosen = np.abs(remaining.astype(np.int64) - chosen).astype(np.int32)
    diffs_to_chosen = np.minimum(diffs_to_chosen, N)
    blocked_by_chosen = used_diffs_arr[diffs_to_chosen].astype(bool)

    # Also check if any |c - s| for s in S[:-1] is now in used_diffs_arr
    # (new diffs might conflict with existing candidate diffs)
    S_prev = np.array(S[:-1], dtype=np.int32)
    if len(S_prev) >= 2:
        # For each remaining candidate, check all diffs with S_prev
        # Vectorized: diffs_mat[i, j] = |remaining[i] - S_prev[j]|
        diffs_mat = np.abs(
            remaining[:, None].astype(np.int64) - S_prev[None, :].astype(np.int64)
        ).astype(np.int32)
        diffs_mat = np.minimum(diffs_mat, N)
        newly_blocked = np.any(used_diffs_arr[diffs_mat], axis=1)
        blocked = blocked_by_chosen | newly_blocked
    else:
        blocked = blocked_by_chosen

    # Also check intra-new-diffs: if any two elements in S give same diff to a candidate
    # This happens when |c - s1| = |c - s2| for s1,s2 in S, i.e., c = (s1+s2)/2
    # Check for mid-points
    S_arr = np.array(S, dtype=np.int32)
    if len(S_arr) >= 2:
        # All pairs in S
        pairs_i, pairs_j = np.triu_indices(len(S_arr), k=1)
        midpoints = (S_arr[pairs_i].astype(np.int64) + S_arr[pairs_j].astype(np.int64))
        # midpoints that are even and in range
        even_mask = (midpoints % 2 == 0)
        midpoints = midpoints[even_mask] // 2
        midpoints = midpoints[(midpoints >= 0) & (midpoints <= N)].astype(np.int32)
        if len(midpoints) > 0:
            mid_set = np.zeros(N + 1, dtype=bool)
            mid_set[midpoints] = True
            blocked |= mid_set[remaining]

    valid_arr[remaining[blocked]] = 0


def _compute_blocking(valid_arr, used_diffs_arr, S_indicator, S, N):
    """
    Compute blocking score for each candidate c in [0,N].
    blocking[c] = count of valid c' that would be blocked by adding c.

    Two components:
    1. base_blocking[c] = Σ_{d in used_diffs} (valid[c+d] + valid[c-d])
       [how many valid candidates share a diff with existing elements via c]
    2. new_blocking[c] = Σ_{s in S} valid[2c - s]  (where 0 <= 2c-s <= N)
       [how many valid candidates would clash with new diffs created by c]
    """
    blocking = np.zeros(N + 1, dtype=np.float32)

    # Component 1: base blocking from used_diffs
    used_d_list = np.nonzero(used_diffs_arr)[0]
    for d in used_d_list:
        d = int(d)
        # valid[c + d] for c = 0 to N-d
        if d <= N:
            blocking[:N + 1 - d] += valid_arr[d:]
            # valid[c - d] for c = d to N
            blocking[d:] += valid_arr[:N + 1 - d]

    # Component 2: new blocking from S elements
    for s in S:
        s = int(s)
        # valid[2c - s] for c in [0, N]
        # 2c - s in [0, N] → c in [ceil(s/2), floor((N+s)/2)]
        c_min = max(0, (s + 1) // 2)
        c_max = min(N, (N + s) // 2)
        if c_min > c_max:
            continue
        c_range = np.arange(c_min, c_max + 1)
        v_range = 2 * c_range - s  # = 2c - s, in [0, N]
        valid_mask = (v_range >= 0) & (v_range <= N)
        blocking[c_range[valid_mask]] += valid_arr[v_range[valid_mask]]

    return blocking


if __name__ == "__main__":
    import sys, time
    sys.path.insert(0, '.')
    from helpers.core import is_sidon

    for N in [200, 1000, 10000]:
        t = time.time()
        S = entrypoint(N=N)
        elapsed = time.time() - t
        valid = is_sidon(S)
        print(f"N={N}: size={len(S)}, valid={valid}, time={elapsed:.2f}s")
        if N <= 200:
            print(f"  Set: {sorted(S)}")
