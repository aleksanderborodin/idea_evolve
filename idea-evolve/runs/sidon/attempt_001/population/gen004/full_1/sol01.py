# fitness: 102
"""
CP-SAT integer formulation for Sidon sets.

Key insight: use integer element variables + all_different on differences.
Much more compact than indicator variables (5356 vars vs ~50M for N=10000, k=103).

Formulation:
- k integer variables e_0 < e_1 < ... < e_{k-1} in {0,...,N}
- C(k,2) difference variables d_{i,j} = e_j - e_i
- AddAllDifferent on differences enforces Sidon condition
- Singer 102 hint warm-starts from the known best

Strategy:
- Attempt k=103, N=10000 with Singer hint (300s)
- If found, attempt k=104
- Fall back to Singer 102 baseline
"""

import sys
import time
from ortools.sat.python import cp_model

# Current best: Singer q=101 set (102 elements in {0,...,10000})
SINGER_102 = [
    0, 129, 385, 586, 624, 844, 938, 1001, 1008, 1104, 1169, 1183, 1186,
    1201, 1212, 1225, 1332, 1420, 1574, 1633, 1679, 1868, 1963, 2075, 2212,
    2235, 2337, 2388, 2479, 2489, 2520, 2547, 2613, 2829, 2849, 2854, 3023,
    3195, 3578, 3635, 3719, 3793, 3805, 3931, 4007, 4268, 4328, 4456, 4518,
    4537, 4571, 4648, 4654, 4721, 4835, 4927, 5002, 5145, 5167, 5366, 5413,
    5666, 5699, 5735, 5789, 5839, 6086, 6094, 6134, 6457, 6492, 6537, 6592,
    6608, 6636, 6714, 6763, 6919, 7052, 7197, 7199, 7489, 7490, 7599, 7686,
    8029, 8093, 8191, 8421, 8506, 8510, 8739, 8776, 8962, 9014, 9075, 9194,
    9266, 9627, 9745, 9766, 9775
]


def solve_sidon_k(k, N, hint=None, time_limit=60, workers=8, verbose=False):
    """
    Try to find a k-element Sidon set in {0,...,N}.

    Returns (sorted list, elapsed_s, status_str) if found,
    or (None, elapsed_s, status_str) if infeasible/timeout.
    """
    model = cp_model.CpModel()

    # Element variables with strict ordering (symmetry breaking)
    e = [model.new_int_var(0, N, f'e{i}') for i in range(k)]
    for i in range(k - 1):
        model.add(e[i] + 1 <= e[i + 1])

    # Difference variables: d_{i,j} = e[j] - e[i]
    diff_vars = []
    for i in range(k):
        for j in range(i + 1, k):
            d = model.new_int_var(1, N, f'd{i}_{j}')
            model.add(d == e[j] - e[i])
            diff_vars.append(d)

    # Sidon condition: all differences are distinct
    model.add_all_different(diff_vars)

    # Warm start hints
    if hint is not None:
        sorted_hint = sorted(hint)
        for i, val in enumerate(sorted_hint[:k]):
            model.add_hint(e[i], val)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    if verbose:
        solver.parameters.log_search_progress = True

    t0 = time.time()
    status = solver.Solve(model)
    elapsed = time.time() - t0

    status_name = solver.StatusName(status)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        sol = sorted([solver.Value(e[i]) for i in range(k)])
        return sol, elapsed, status_name
    return None, elapsed, status_name


def verify_sidon(S):
    """Verify that S is a valid Sidon set."""
    S = sorted(S)
    diffs = [S[j] - S[i] for i in range(len(S)) for j in range(i + 1, len(S))]
    return len(diffs) == len(set(diffs))


def entrypoint():
    N = 10000
    best = list(SINGER_102)
    best_size = len(best)  # 102

    # Phase 1: Try k=103 with Singer hint (main ILP attempt)
    print(f"[ILP] Attempting k=103, N={N} with Singer hint (300s)...", file=sys.stderr)
    t_start = time.time()
    sol103, t103, st103 = solve_sidon_k(103, N, hint=SINGER_102, time_limit=300, workers=8)
    print(f"[ILP] k=103: {st103} in {t103:.1f}s", file=sys.stderr)

    if sol103 is not None:
        if verify_sidon(sol103):
            print(f"[ILP] Found valid 103-element set!", file=sys.stderr)
            best = sol103
            best_size = 103

            # Phase 2: Try k=104 with the 103-element result as hint
            remaining_budget = 600 - (time.time() - t_start)
            if remaining_budget > 30:
                print(f"[ILP] Attempting k=104 ({remaining_budget:.0f}s budget)...", file=sys.stderr)
                sol104, t104, st104 = solve_sidon_k(104, N, hint=sol103,
                                                     time_limit=int(remaining_budget),
                                                     workers=8)
                print(f"[ILP] k=104: {st104} in {t104:.1f}s", file=sys.stderr)
                if sol104 is not None and verify_sidon(sol104):
                    best = sol104
                    best_size = 104
        else:
            print(f"[ILP] WARNING: found solution failed verify_sidon check!", file=sys.stderr)

    elif st103 == "INFEASIBLE":
        print(f"[ILP] PROVEN: no 103-element Sidon set in {{0,...,{N}}} exists!", file=sys.stderr)
    else:
        # UNKNOWN (timeout) — try without hints in remaining time
        remaining = 600 - (time.time() - t_start)
        if remaining > 60:
            print(f"[ILP] Trying k=103 without hints ({remaining:.0f}s)...", file=sys.stderr)
            sol103b, t103b, st103b = solve_sidon_k(103, N, hint=None,
                                                    time_limit=int(remaining),
                                                    workers=8)
            print(f"[ILP] k=103 (no hints): {st103b} in {t103b:.1f}s", file=sys.stderr)
            if sol103b is not None and verify_sidon(sol103b):
                best = sol103b
                best_size = 103

    print(f"[ILP] Best result: {best_size} elements", file=sys.stderr)
    assert verify_sidon(best), "Final solution failed Sidon check!"
    assert all(0 <= x <= N for x in best), "Element out of range!"
    return best
