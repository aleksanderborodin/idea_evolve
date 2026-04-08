# fitness: TBD
"""
CP-SAT k=106 with 105-mark warm-start.
Phase 1: Verify formulation with k=104 (instant with hint).
Phase 2: k=106 main run (1200s, 16 workers).
Phase 3: k=106 with linearization_level=2, symmetry_level=2 (if time remains).
Falls back to 105-mark set if no improvement found.
"""

import time
import sys

KNOWN_105 = [0, 12, 200, 213, 235, 296, 402, 468, 473, 513, 725, 854, 855, 964, 1018, 1059, 1209, 1375, 1392, 1578, 1657, 1664, 1907, 1974, 2048, 2087, 2208, 2285, 2295, 2695, 2793, 2818, 2842, 2868, 2969, 2975, 3074, 3112, 3130, 3190, 3194, 3322, 3640, 3654, 3683, 4066, 4081, 4128, 4277, 4342, 4358, 4411, 4431, 4523, 4662, 4698, 4717, 4820, 5239, 5291, 5323, 5381, 5408, 5683, 5839, 5992, 6026, 6034, 6219, 6365, 6441, 6509, 6589, 6768, 6952, 7009, 7161, 7358, 7446, 7565, 7624, 7823, 7860, 7893, 7923, 8228, 8231, 8259, 8390, 8399, 8653, 8697, 8823, 8871, 8917, 8968, 9330, 9402, 9520, 9644, 9655, 9746, 9748, 9769, 9884]


def solve_cpsat(k, N, hint, time_limit, num_workers=16, verbose=True, extra_params=None):
    """Integer element formulation: k ordered vars, AllDifferent on differences."""
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()

    # k ordered integer variables in [0, N]
    x = [model.new_int_var(0, N, f'x_{i}') for i in range(k)]

    # Strict ordering (breaks symmetry)
    for i in range(k - 1):
        model.add(x[i + 1] > x[i])

    # Difference variables: d[i][j] = x[j] - x[i] for all i < j
    diffs = []
    for i in range(k):
        for j in range(i + 1, k):
            d = model.new_int_var(1, N, f'd_{i}_{j}')
            model.add(d == x[j] - x[i])
            diffs.append(d)

    # Sidon property: all pairwise differences must be distinct
    model.add_all_different(diffs)

    # Warm-start hint
    if hint:
        h = sorted(hint)
        for i in range(min(len(h), k)):
            model.add_hint(x[i], h[i])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = num_workers
    solver.parameters.log_search_progress = verbose
    if extra_params:
        for attr, val in extra_params.items():
            setattr(solver.parameters, attr, val)

    t0 = time.time()
    status = solver.solve(model)
    elapsed = time.time() - t0

    status_name = solver.status_name(status)
    result = {'status': status_name, 'k': k, 'time': elapsed}

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        sol = sorted([solver.value(x[i]) for i in range(k)])
        result['solution'] = sol
        result['size'] = len(sol)
        # Verify it's actually Sidon
        dset = set()
        valid = True
        s = sorted(sol)
        for a in range(len(s)):
            for b in range(a + 1, len(s)):
                d = s[b] - s[a]
                if d in dset:
                    valid = False
                    break
                dset.add(d)
            if not valid:
                break
        result['verified_sidon'] = valid

    return result


def entrypoint():
    N = 10000
    hint = KNOWN_105
    best = list(hint)
    t_session_start = time.time()

    # Phase 1: Verify formulation with k=104
    print("=== Phase 1: Verify formulation k=104 (30s limit) ===", flush=True)
    r104 = solve_cpsat(104, N, hint, time_limit=30, num_workers=8, verbose=False)
    elapsed104 = r104['time']
    print(f"k=104: {r104['status']} in {elapsed104:.1f}s", flush=True)
    if r104.get('solution'):
        print(f"  -> Found {r104['size']} elements (verified={r104.get('verified_sidon')})", flush=True)
    else:
        print(f"  -> No solution (formulation may have issue)", flush=True)

    # Phase 2: k=106 main run
    print("\n=== Phase 2: k=106 with 105-mark hint (1200s) ===", flush=True)
    r106 = solve_cpsat(106, N, hint, time_limit=1200, num_workers=16, verbose=True)
    elapsed106 = r106['time']
    print(f"\nk=106: {r106['status']} in {elapsed106:.1f}s", flush=True)
    if r106.get('solution') and r106['verified_sidon']:
        print(f"  -> FOUND {r106['size']} elements!", flush=True)
        print(f"  -> {r106['solution']}", flush=True)
        best = r106['solution']
        return sorted(best)
    else:
        print(f"  -> No feasible k=106 found", flush=True)

    # Phase 3: k=106 with enhanced parameters (if time permits)
    session_elapsed = time.time() - t_session_start
    remaining = 2400 - session_elapsed  # Leave time for reporting
    if remaining > 300:
        print(f"\n=== Phase 3: k=106 with linearization_level=2 ({min(600, int(remaining-120))}s) ===", flush=True)
        r106b = solve_cpsat(
            106, N, hint,
            time_limit=min(600, int(remaining - 120)),
            num_workers=16,
            verbose=True,
            extra_params={'linearization_level': 2, 'symmetry_level': 2}
        )
        print(f"\nk=106 (enhanced): {r106b['status']} in {r106b['time']:.1f}s", flush=True)
        if r106b.get('solution') and r106b.get('verified_sidon'):
            print(f"  -> FOUND {r106b['size']} elements!", flush=True)
            best = r106b['solution']
            return sorted(best)

    print(f"\nTotal session time: {time.time() - t_session_start:.1f}s", flush=True)
    print("No improvement found. Returning 105-mark set.", flush=True)
    return sorted(best)
