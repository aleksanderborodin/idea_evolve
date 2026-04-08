"""
Singer+1 Structure Analysis for Sidon Sets.

For small primes q, finds the optimal Sidon set in {0,...,q^2+q} and compares
to the Singer difference set. Analyzes the structure of "extra" elements.
"""
import sys
import time
from ortools.sat.python import cp_model

# Ensure helpers are importable
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon')

from helpers.singer import find_singer_set


def solve_sidon_optimal(N, time_limit=120, workers=8, verbose=False):
    """
    Find the MAXIMUM Sidon set in {0,...,N} using CP-SAT indicator formulation.
    Returns (optimal_set, elapsed_s, status_str).
    """
    model = cp_model.CpModel()

    # x[i] = 1 if i is in the set
    x = [model.new_bool_var(f'x{i}') for i in range(N + 1)]

    # For each pair (i, j) with i < j, the difference d = j - i
    # Constraint: at most one pair can realize each difference d
    # For each d in 1..N, collect all (i, j) pairs with j - i = d:
    # x[i] + x[j] <= 1 is too weak for Sidon. We need AllDifferent on differences.

    # Actually: Sidon property means for each d, sum_{i: i+d <= N} x[i]*x[i+d] <= 1
    for d in range(1, N + 1):
        # Sum over all pairs (i, i+d): x[i] AND x[i+d]
        pair_vars = []
        for i in range(N + 1 - d):
            # Create an auxiliary variable: z = x[i] AND x[i+d]
            z = model.new_bool_var(f'z_{d}_{i}')
            model.add_bool_and([x[i], x[i + d]]).only_enforce_if(z)
            model.add_bool_or([x[i].negated(), x[i + d].negated()]).only_enforce_if(z.negated())
            pair_vars.append(z)
        if pair_vars:
            model.add(sum(pair_vars) <= 1)

    # Maximize number of elements
    model.maximize(sum(x))

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
        sol = [i for i in range(N + 1) if solver.Value(x[i]) == 1]
        return sol, elapsed, status_name
    return None, elapsed, status_name


def solve_sidon_k(k, N, hint=None, time_limit=60, workers=8, verbose=False):
    """
    Try to find a k-element Sidon set in {0,...,N} using integer element formulation.
    Much faster than indicator formulation for checking feasibility at specific k.
    """
    model = cp_model.CpModel()
    e = [model.new_int_var(0, N, f'e{i}') for i in range(k)]
    for i in range(k - 1):
        model.add(e[i] + 1 <= e[i + 1])

    diff_vars = []
    for i in range(k):
        for j in range(i + 1, k):
            d = model.new_int_var(1, N, f'd{i}_{j}')
            model.add(d == e[j] - e[i])
            diff_vars.append(d)

    model.add_all_different(diff_vars)

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


def analyze_structure(optimal_set, singer_set, q, N):
    """
    Analyze the structure of optimal set vs Singer set.
    Returns a dict with analysis results.
    """
    singer_elems = set(singer_set)
    optimal_elems = set(optimal_set)

    in_both = singer_elems & optimal_elems
    only_in_singer = singer_elems - optimal_elems
    only_in_optimal = optimal_elems - singer_elems

    # Singer differences
    singer_diffs = set()
    singer_sorted = sorted(singer_set)
    for i in range(len(singer_sorted)):
        for j in range(i + 1, len(singer_sorted)):
            singer_diffs.add(singer_sorted[j] - singer_sorted[i])

    # Optimal differences
    optimal_sorted = sorted(optimal_set)
    optimal_diffs = set()
    for i in range(len(optimal_sorted)):
        for j in range(i + 1, len(optimal_sorted)):
            optimal_diffs.add(optimal_sorted[j] - optimal_sorted[i])

    # For extra elements, what are their new differences?
    extra_elems = sorted(only_in_optimal)
    extra_diff_info = {}
    for e in extra_elems:
        new_diffs_from_extra = set()
        # differences between extra element and singer elements that ARE in optimal
        for s in optimal_sorted:
            if s != e:
                new_diffs_from_extra.add(abs(e - s))
        extra_diff_info[e] = new_diffs_from_extra

    # What differences are used only by Singer (not in optimal)?
    singer_only_diffs = singer_diffs - optimal_diffs

    # What differences are new in optimal (not in Singer)?
    optimal_only_diffs = optimal_diffs - singer_diffs

    # Check if extra elements use "free" differences (those unused by Singer)
    free_diffs_in_range = set(range(1, N + 1)) - singer_diffs

    return {
        'q': q, 'N': N,
        'singer_size': len(singer_set),
        'optimal_size': len(optimal_set),
        'overlap': len(in_both),
        'only_in_singer': sorted(only_in_singer),
        'extra_elements': extra_elems,
        'singer_diffs_count': len(singer_diffs),
        'free_diffs_count': len(free_diffs_in_range),
        'extra_diff_info': extra_diff_info,
        'extra_uses_free_diffs': all(
            new_diffs_from_extra <= free_diffs_in_range
            for new_diffs_from_extra in extra_diff_info.values()
        ) if extra_elems else None,
    }


def main():
    cases = [
        (7, 56),    # q=7, N=q^2+q = 56 (Singer=8, ILP expected=10)
        (11, 132),  # q=11, N=132 (Singer=12, ILP expected=13)
        (17, 306),  # q=17, N=306 (Singer=18, ILP=?)
        (23, 552),  # q=23, N=552 (Singer=24, ILP=?)
    ]

    results = []

    for q, N in cases:
        print(f"\n{'='*60}", flush=True)
        print(f"q={q}, N={N} (Singer should give {q+1} elements)", flush=True)

        # Get Singer set
        singer = find_singer_set(q)
        # Singer set is in Z_{q^2+q+1}, we need to truncate to [0, N]
        singer_in_range = [s for s in singer if s <= N]
        print(f"Singer set size: {len(singer)} (in Z_{q**2+q+1}), {len(singer_in_range)} in [0,{N}]", flush=True)

        # Find optimal using integer element formulation
        # Start from Singer size and search upward
        optimal_set = singer_in_range[:]
        optimal_k = len(singer_in_range)

        # Try increasing k
        for k_try in range(optimal_k + 1, optimal_k + 5):
            time_limit = 60 if q <= 11 else 120
            print(f"  Trying k={k_try}...", flush=True)
            t0 = time.time()
            sol, elapsed, status = solve_sidon_k(k_try, N, hint=optimal_set,
                                                  time_limit=time_limit, workers=8)
            print(f"  k={k_try}: {status} in {elapsed:.1f}s", flush=True)
            if sol is not None:
                optimal_set = sol
                optimal_k = k_try
                print(f"  Found k={k_try}: {sol}", flush=True)
            else:
                if status == "INFEASIBLE":
                    print(f"  k={k_try} proved INFEASIBLE — optimal is {optimal_k}", flush=True)
                    break
                else:
                    print(f"  k={k_try} UNKNOWN after {elapsed:.1f}s — moving on", flush=True)
                    break

        analysis = analyze_structure(optimal_set, singer_in_range, q, N)
        results.append(analysis)

        print(f"\nResults for q={q}, N={N}:", flush=True)
        print(f"  Singer: {len(singer_in_range)} elements", flush=True)
        print(f"  Optimal found: {len(optimal_set)} elements", flush=True)
        print(f"  Overlap with Singer: {analysis['overlap']}", flush=True)
        print(f"  Extra elements: {analysis['extra_elements']}", flush=True)
        print(f"  Elements only in Singer: {analysis['only_in_singer']}", flush=True)
        print(f"  Singer uses {analysis['singer_diffs_count']} of {N} differences", flush=True)
        print(f"  Free differences (unused by Singer): {analysis['free_diffs_count']}", flush=True)
        print(f"  Extra elements use only free diffs: {analysis['extra_uses_free_diffs']}", flush=True)

    return results


if __name__ == '__main__':
    results = main()
    print("\n\nSUMMARY:", flush=True)
    for r in results:
        print(f"q={r['q']}, N={r['N']}: Singer={r['singer_size']}, Optimal={r['optimal_size']}, "
              f"Extra={r['extra_elements']}, Uses free diffs only: {r['extra_uses_free_diffs']}", flush=True)
