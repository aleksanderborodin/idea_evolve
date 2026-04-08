# fitness: TBD
"""
VLNS (Very Large Neighborhood Search) for Sidon sets.
Strategy: Remove 20 elements from the 105-mark set, then use CP-SAT to find 21
replacements — a much smaller subproblem than the full k=106 problem.

Key insight: Instead of searching for 106 elements from scratch (CP-SAT always returns
UNKNOWN), fix 85 elements and only search for 21. The free variables have constrained
domains (must not conflict with fixed differences), making CP-SAT much faster.

Multiple random removals are tried with 120s budget each.
Falls back to 105-mark set if nothing better found.
"""

import time
import random

KNOWN_105 = [0, 12, 200, 213, 235, 296, 402, 468, 473, 513, 725, 854, 855, 964, 1018, 1059, 1209, 1375, 1392, 1578, 1657, 1664, 1907, 1974, 2048, 2087, 2208, 2285, 2295, 2695, 2793, 2818, 2842, 2868, 2969, 2975, 3074, 3112, 3130, 3190, 3194, 3322, 3640, 3654, 3683, 4066, 4081, 4128, 4277, 4342, 4358, 4411, 4431, 4523, 4662, 4698, 4717, 4820, 5239, 5291, 5323, 5381, 5408, 5683, 5839, 5992, 6026, 6034, 6219, 6365, 6441, 6509, 6589, 6768, 6952, 7009, 7161, 7358, 7446, 7565, 7624, 7823, 7860, 7893, 7923, 8228, 8231, 8259, 8390, 8399, 8653, 8697, 8823, 8871, 8917, 8968, 9330, 9402, 9520, 9644, 9655, 9746, 9748, 9769, 9884]


def make_domain_excluding(N, forbidden_set):
    """Create sorted list of intervals [1,N] excluding forbidden values."""
    from ortools.sat.python import cp_model
    forbidden_sorted = sorted(forbidden_set)
    intervals = []
    prev = 0
    for v in forbidden_sorted:
        if v < 1 or v > N:
            continue
        if prev + 1 <= v - 1:
            intervals.append([prev + 1, v - 1])
        prev = v
    if prev + 1 <= N:
        intervals.append([prev + 1, N])
    if not intervals:
        return cp_model.Domain(1, 1)
    flat = []
    for lo, hi in intervals:
        flat.extend([lo, hi])
    return cp_model.Domain.from_flat_intervals(flat)


def vlns_cpsat(fixed, n_free, N=10000, time_limit=120, num_workers=8, verbose=False):
    """
    Given 'fixed' elements (a valid Sidon subset), find 'n_free' additional elements
    that together with 'fixed' form a valid Sidon set of size len(fixed)+n_free.

    Returns: (status_name, solution_or_None, elapsed)
    """
    from ortools.sat.python import cp_model

    fixed = sorted(fixed)
    n_fixed = len(fixed)
    fixed_set = set(fixed)

    # Compute all differences within fixed elements
    fixed_diffs = set()
    for i in range(n_fixed):
        for j in range(i + 1, n_fixed):
            fixed_diffs.add(fixed[j] - fixed[i])

    model = cp_model.CpModel()

    # Domain for free variables: [0,N] excluding fixed elements
    fixed_excl_domain = cp_model.Domain.from_flat_intervals([0, N])
    for fv in sorted(fixed_set):
        fixed_excl_domain = fixed_excl_domain.intersection_with(
            cp_model.Domain.from_flat_intervals([0, fv - 1, fv + 1, N]) if 0 < fv < N
            else (cp_model.Domain.from_flat_intervals([1, N]) if fv == 0
                  else cp_model.Domain.from_flat_intervals([0, N - 1]))
        )

    # Simpler: just create free vars with domain [0,N] and add != constraints for fixed
    # (CP-SAT handles bounded domains efficiently)
    y = [model.new_int_var(0, N, f'y_{i}') for i in range(n_free)]

    # Free vars must not equal any fixed element
    for yi in y:
        for fv in fixed:
            model.add(yi != fv)

    # Free vars must not equal each other (implicit in ordering below)
    # Strict ordering to break symmetry
    for i in range(n_free - 1):
        model.add(y[i + 1] > y[i])

    # Domain for difference variables: [1,N] excluding fixed_diffs
    diff_domain = make_domain_excluding(N, fixed_diffs)

    # Differences between free variables
    free_diffs = []
    for i in range(n_free):
        for j in range(i + 1, n_free):
            d = model.new_int_var_from_domain(diff_domain, f'ff_{i}_{j}')
            model.add(d == y[j] - y[i])
            free_diffs.append(d)

    # Differences between free vars and fixed vars (absolute value)
    cross_diffs = []
    for i in range(n_free):
        for fv in fixed:
            d = model.new_int_var_from_domain(diff_domain, f'cf_{i}_{fv}')
            model.add_abs_equality(d, y[i] - fv)
            cross_diffs.append(d)

    # All new differences (free-free + cross) must be distinct AND not in fixed_diffs
    # (domain already excludes fixed_diffs, so just need AllDifferent among themselves)
    all_new_diffs = free_diffs + cross_diffs
    model.add_all_different(all_new_diffs)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = num_workers
    solver.parameters.log_search_progress = verbose

    t0 = time.time()
    status = solver.solve(model)
    elapsed = time.time() - t0

    status_name = solver.status_name(status)

    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        new_elems = sorted([solver.value(y[i]) for i in range(n_free)])
        full_sol = sorted(fixed + new_elems)
        # Verify
        dset = set()
        valid = True
        for a in range(len(full_sol)):
            for b in range(a + 1, len(full_sol)):
                d = full_sol[b] - full_sol[a]
                if d in dset:
                    valid = False
                    break
                dset.add(d)
            if not valid:
                break
        if valid:
            return status_name, full_sol, elapsed
        else:
            return status_name + '_INVALID', None, elapsed

    return status_name, None, elapsed


def entrypoint():
    N = 10000
    S = sorted(KNOWN_105)
    n = len(S)
    best = list(S)
    best_size = n

    t_start = time.time()
    time_limit_total = 1500  # Total budget for this approach

    rng = random.Random(42)

    # Try multiple removal patterns
    trial_configs = [
        # (n_remove, description)
        (20, 'random-20'),
        (20, 'random-20'),
        (20, 'random-20'),
        (15, 'random-15'),
        (15, 'random-15'),
        (25, 'random-25'),
        (25, 'random-25'),
        (20, 'high-density-20'),  # Remove densely-packed elements
        (20, 'spread-20'),        # Remove spread-out elements
    ]

    for trial_idx, (n_remove, desc) in enumerate(trial_configs):
        elapsed_total = time.time() - t_start
        if elapsed_total > time_limit_total - 60:
            print(f"Time limit approaching, stopping trials.", flush=True)
            break

        n_free = n_remove + 1  # Need to find n_remove+1 to get 106 total

        # Choose which elements to remove
        if 'high-density' in desc:
            # Remove elements that are close together (dense regions)
            # Compute inter-element gaps and remove from smallest-gap regions
            gaps = [(S[i+1] - S[i], i) for i in range(len(S)-1)]
            gaps.sort()  # smallest gaps first
            # Remove elements at smallest gaps
            remove_indices = set()
            for _, idx in gaps:
                remove_indices.add(idx)
                remove_indices.add(idx + 1)
                if len(remove_indices) >= n_remove:
                    break
            remove_set = {S[i] for i in remove_indices}
            if len(remove_set) < n_remove:
                # Fill up with random
                remaining = [x for x in S if x not in remove_set]
                extra = rng.sample(remaining, n_remove - len(remove_set))
                remove_set.update(extra)
        elif 'spread' in desc:
            # Remove evenly spread elements
            step = n // n_remove
            remove_indices = list(range(0, n, step))[:n_remove]
            remove_set = {S[i] for i in remove_indices}
        else:
            # Random removal
            remove_set = set(rng.sample(S, n_remove))

        fixed = [x for x in S if x not in remove_set]

        time_per_trial = min(120, (time_limit_total - elapsed_total - 60) // max(1, len(trial_configs) - trial_idx))
        time_per_trial = max(30, time_per_trial)

        print(f"\nTrial {trial_idx+1} ({desc}): removing {n_remove} elements, "
              f"finding {n_free} replacements, {time_per_trial:.0f}s budget", flush=True)
        print(f"  Fixed: {len(fixed)} elements", flush=True)
        print(f"  Removed: {sorted(remove_set)}", flush=True)

        status, sol, elapsed = vlns_cpsat(
            fixed, n_free, N=N,
            time_limit=time_per_trial,
            num_workers=8,
            verbose=True
        )

        print(f"  Result: {status} in {elapsed:.1f}s", flush=True)
        if sol is not None:
            print(f"  -> FOUND {len(sol)} elements!", flush=True)
            print(f"  -> {sol}", flush=True)
            if len(sol) > best_size:
                best = sol
                best_size = len(sol)
                if best_size >= 106:
                    print(f"\n*** BREAKTHROUGH: {best_size} elements found! ***", flush=True)
                    break

    print(f"\nTotal VLNS time: {time.time() - t_start:.1f}s", flush=True)
    print(f"Best found: {best_size}", flush=True)
    return sorted(best)
