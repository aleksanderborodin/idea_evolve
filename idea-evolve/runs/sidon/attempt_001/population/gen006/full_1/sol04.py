# fitness: TBD
"""
Binary search on N: find the minimum N for which a Sidon set of size k=106 is feasible.
Tests N in [10000, 10500, 11000, 12000, 15000, 20000] with 120s CP-SAT each.
If k=106 is feasible for some N > 10000, records the minimum such N.
Falls back to 105-mark set.
"""

import time

KNOWN_105 = [0, 12, 200, 213, 235, 296, 402, 468, 473, 513, 725, 854, 855, 964, 1018, 1059, 1209, 1375, 1392, 1578, 1657, 1664, 1907, 1974, 2048, 2087, 2208, 2285, 2295, 2695, 2793, 2818, 2842, 2868, 2969, 2975, 3074, 3112, 3130, 3190, 3194, 3322, 3640, 3654, 3683, 4066, 4081, 4128, 4277, 4342, 4358, 4411, 4431, 4523, 4662, 4698, 4717, 4820, 5239, 5291, 5323, 5381, 5408, 5683, 5839, 5992, 6026, 6034, 6219, 6365, 6441, 6509, 6589, 6768, 6952, 7009, 7161, 7358, 7446, 7565, 7624, 7823, 7860, 7893, 7923, 8228, 8231, 8259, 8390, 8399, 8653, 8697, 8823, 8871, 8917, 8968, 9330, 9402, 9520, 9644, 9655, 9746, 9748, 9769, 9884]


def solve_cpsat_k(k, N, hint, time_limit, num_workers=8):
    """Solve for Sidon set of size exactly k in [0,N]. Returns (status, solution_or_None, elapsed)."""
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()

    x = [model.new_int_var(0, N, f'x_{i}') for i in range(k)]
    for i in range(k - 1):
        model.add(x[i + 1] > x[i])

    diffs = []
    for i in range(k):
        for j in range(i + 1, k):
            d = model.new_int_var(1, N, f'd_{i}_{j}')
            model.add(d == x[j] - x[i])
            diffs.append(d)
    model.add_all_different(diffs)

    if hint:
        h = sorted(hint)
        # Scale hint to fit within N
        if h[-1] > N:
            scale = N / h[-1]
            scaled = [int(v * scale) for v in h]
            # Ensure distinct and ordered
            seen = set()
            hh = []
            for v in scaled:
                while v in seen:
                    v += 1
                if v <= N:
                    seen.add(v)
                    hh.append(v)
            hint_to_use = hh[:k]
        else:
            hint_to_use = h[:k]
        for i in range(min(len(hint_to_use), k)):
            model.add_hint(x[i], hint_to_use[i])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = num_workers
    solver.parameters.log_search_progress = False

    t0 = time.time()
    status = solver.solve(model)
    elapsed = time.time() - t0

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        sol = sorted([solver.value(x[i]) for i in range(k)])
        return solver.status_name(status), sol, elapsed

    return solver.status_name(status), None, elapsed


def entrypoint():
    best = list(KNOWN_105)
    best_size = 105
    t_start = time.time()

    # Test N values for k=106 feasibility
    # Start at N=10000 (our target), then expand
    n_values = [10000, 10200, 10500, 11000, 12000, 15000, 20000]

    print("Binary search on N: find minimum N for k=106 feasibility", flush=True)
    print(f"Testing N values: {n_values}", flush=True)
    print(f"Budget: 120s per N value\n", flush=True)

    min_feasible_N = None

    for N in n_values:
        elapsed_total = time.time() - t_start
        if elapsed_total > 900:
            print(f"Session time limit approaching, stopping.", flush=True)
            break

        print(f"Testing N={N}...", flush=True)
        status, sol, elapsed = solve_cpsat_k(
            k=106, N=N, hint=KNOWN_105,
            time_limit=120, num_workers=8
        )
        print(f"  N={N}: {status} in {elapsed:.1f}s", flush=True)

        if sol is not None:
            # Verify it's a valid Sidon set
            dset = set()
            valid = True
            for a in range(len(sol)):
                for b in range(a + 1, len(sol)):
                    d = sol[b] - sol[a]
                    if d in dset:
                        valid = False
                        break
                    dset.add(d)
                if not valid:
                    break

            if valid:
                print(f"  -> FEASIBLE k=106 at N={N}! (verified Sidon)", flush=True)
                if min_feasible_N is None:
                    min_feasible_N = N
                # If N=10000, this is our target — update best!
                if N == 10000 and len(sol) > best_size:
                    best = sol
                    best_size = len(sol)
                    print(f"  -> Updated best to {best_size}!", flush=True)
                    break  # Found it!
            else:
                print(f"  -> CP-SAT returned FEASIBLE but set is not valid Sidon! Bug?", flush=True)
        else:
            print(f"  -> Not feasible within {elapsed:.1f}s (may need longer)", flush=True)

    if min_feasible_N is not None:
        print(f"\nMinimum feasible N for k=106: {min_feasible_N}", flush=True)
    else:
        print(f"\nNo feasible N found for k=106 within time budget", flush=True)

    print(f"Total time: {time.time() - t_start:.1f}s", flush=True)
    return sorted(best)
