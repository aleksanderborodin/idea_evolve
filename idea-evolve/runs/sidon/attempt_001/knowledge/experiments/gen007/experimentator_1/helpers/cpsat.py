"""CP-SAT helpers for Sidon set optimization.

Provides reusable CP-SAT formulations for finding and improving Sidon sets.
All functions return result dicts with status, solution, size, and timing.

Usage:
    from helpers.cpsat import solve_sidon_cpsat, vlns_sidon, vlns_batch

Functions:
    solve_sidon_cpsat(k, N, hint, time_limit, num_workers) — find a Sidon set
    vlns_sidon(fixed_elements, n_free, N, time_limit, num_workers) — VLNS refinement
    vlns_batch(base_set, removal_sizes, n_trials_per_size, N, ...) — batch VLNS trials
    self_test() — verify all functions produce valid Sidon sets
"""

import time
import random
from collections import defaultdict
from ortools.sat.python import cp_model


def _status_name(status):
    """Convert CP-SAT status code to string."""
    return {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.UNKNOWN: "UNKNOWN",
    }.get(status, f"STATUS_{status}")


def solve_sidon_cpsat(k=None, N=10000, hint=None, time_limit=300, num_workers=8):
    """Find a Sidon set in {0,...,N} using CP-SAT.

    For N <= 500: binary variable formulation (x_i in {0,1} per element,
    at-most-one pair indicator per difference value).
    For N > 500: element formulation with pairwise != on differences
    (NOT AllDifferent — uses decomposed != constraints instead).

    Args:
        k: Optional minimum set size (sum(x_i) >= k). If None, just maximizes.
        N: Upper bound of range {0,...,N}. Default 10000.
        hint: Optional list of integers for CP-SAT SolutionHint.
        time_limit: Solver time limit in seconds. Default 300.
        num_workers: Number of parallel workers. Default 8.

    Returns:
        dict: {status, solution, size, time_s}
    """
    t0 = time.time()
    if N <= 500:
        return _solve_binary(k, N, hint, time_limit, num_workers, t0)
    else:
        return _solve_element(k, N, hint, time_limit, num_workers, t0)


def _solve_binary(k, N, hint, time_limit, num_workers, t0):
    """Binary variable formulation — practical for N <= ~500."""
    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x_{i}") for i in range(N + 1)]

    if k is not None:
        model.add(sum(x) >= k)
    model.maximize(sum(x))

    # Sidon: for each difference d, at most one pair (i, i+d) has both in set.
    for d in range(1, N + 1):
        n_pairs = N - d + 1
        if n_pairs < 2:
            continue
        p = []
        for i in range(n_pairs):
            pi = model.new_bool_var(f"p_{i}_{d}")
            model.add_implication(pi, x[i])
            model.add_implication(pi, x[i + d])
            model.add_bool_or([pi, x[i].negated(), x[i + d].negated()])
            p.append(pi)
        model.add_at_most_one(p)

    if hint is not None:
        hint_set = set(hint)
        for i in range(N + 1):
            model.add_hint(x[i], 1 if i in hint_set else 0)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = num_workers
    status = solver.solve(model)

    solution = None
    size = 0
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        solution = sorted(i for i in range(N + 1) if solver.value(x[i]))
        size = len(solution)

    return {"status": _status_name(status), "solution": solution,
            "size": size, "time_s": round(time.time() - t0, 3)}


def _solve_element(k, N, hint, time_limit, num_workers, t0):
    """Element formulation with pairwise != on differences.

    Variables: e_0 < e_1 < ... < e_{k-1} in {0,...,N}.
    Differences d_{ij} = e_j - e_i, all pairwise distinct via != constraints.
    """
    if k is None:
        # Iterative maximization: try increasing k until infeasible/timeout
        start_k = len(hint) if hint else int(N ** 0.5)
        best_result = None
        current_k = start_k
        remaining = time_limit

        while remaining > 5:
            alloc = min(remaining * 0.5, remaining - 5)
            r = _solve_element(current_k, N, hint, alloc, num_workers, t0)
            remaining = time_limit - (time.time() - t0)

            if r["status"] in ("OPTIMAL", "FEASIBLE"):
                best_result = r
                current_k = r["size"] + 1
                hint = r["solution"]
            else:
                break

        if best_result:
            best_result["time_s"] = round(time.time() - t0, 3)
            return best_result
        return {"status": "UNKNOWN", "solution": None, "size": 0,
                "time_s": round(time.time() - t0, 3)}

    model = cp_model.CpModel()
    e = [model.new_int_var(0, N, f"e_{i}") for i in range(k)]
    for i in range(k - 1):
        model.add(e[i + 1] > e[i])

    # Pairwise differences, all distinct via != (not AllDifferent)
    diffs = {}
    for i in range(k):
        for j in range(i + 1, k):
            d = model.new_int_var(1, N, f"d_{i}_{j}")
            model.add(d == e[j] - e[i])
            diffs[(i, j)] = d

    diff_list = list(diffs.values())
    for i in range(len(diff_list)):
        for j in range(i + 1, len(diff_list)):
            model.add(diff_list[i] != diff_list[j])

    if hint is not None:
        hint_sorted = sorted(hint)
        for i in range(min(k, len(hint_sorted))):
            model.add_hint(e[i], hint_sorted[i])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = num_workers
    status = solver.solve(model)

    solution = None
    size = 0
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        solution = sorted(solver.value(e[i]) for i in range(k))
        size = len(solution)

    return {"status": _status_name(status), "solution": solution,
            "size": size, "time_s": round(time.time() - t0, 3)}


def vlns_sidon(fixed_elements, n_free, N=10000, time_limit=120, num_workers=8):
    """Very Large Neighborhood Search: fix some elements, find replacements via CP-SAT.

    Binary formulation on candidate elements. For each difference value d,
    a unified at-most-one constraint covers BOTH free-to-fixed and free-to-free
    diff sources, preventing the gen-6 domain bug.

    Args:
        fixed_elements: list[int] — elements to keep (must be valid Sidon subset).
        n_free: int — max number of free elements to place.
        N: int — upper bound of range {0,...,N}. Default 10000.
        time_limit: float — solver time limit in seconds. Default 120.
        num_workers: int — parallel workers. Default 8.

    Returns:
        dict: {status, solution, size, time_s, fixed_count, free_count}
    """
    t0 = time.time()
    fixed = sorted(set(fixed_elements))
    fixed_set = set(fixed)

    # Validate fixed elements form a valid Sidon set
    fixed_diffs = set()
    for i in range(len(fixed)):
        for j in range(i + 1, len(fixed)):
            d = fixed[j] - fixed[i]
            if d in fixed_diffs:
                return {"status": "MODEL_INVALID", "solution": None, "size": 0,
                        "time_s": round(time.time() - t0, 3),
                        "fixed_count": len(fixed), "free_count": 0,
                        "error": "Fixed elements are not a valid Sidon set"}
            fixed_diffs.add(d)

    model = cp_model.CpModel()

    # Binary var for each candidate (not in fixed set)
    candidates = [i for i in range(N + 1) if i not in fixed_set]
    y = {c: model.new_bool_var(f"y_{c}") for c in candidates}

    model.add(sum(y[c] for c in candidates) <= n_free)
    model.maximize(sum(y[c] for c in candidates))

    # Pre-filter candidates: compute diffs with all fixed elements.
    # A candidate is viable only if:
    #   (a) no diff matches a fixed-fixed diff
    #   (b) all its diffs with fixed elements are distinct
    viable = []
    cand_fixed_diffs = {}  # c -> set of diff values with fixed elements

    for c in candidates:
        diffs_c = set()
        ok = True
        for f in fixed:
            d = abs(c - f)
            if d in fixed_diffs or d in diffs_c:
                ok = False
                break
            diffs_c.add(d)
        if ok:
            viable.append(c)
            cand_fixed_diffs[c] = diffs_c
        else:
            model.add(y[c] == 0)

    # --- Unified per-difference-value constraints ---
    #
    # For each diff value d (not in fixed_diffs), collect all "sources":
    #   Type 2 (free-to-fixed): candidate c where d in cand_fixed_diffs[c].
    #     Active when y[c] = 1.
    #   Type 3 (free-to-free): pair (c1,c2) of viable candidates with |c1-c2| = d.
    #     Active when y[c1] = 1 AND y[c2] = 1.
    #
    # Constraint: at most one source active per diff value.

    # Build type-2 index
    type2 = defaultdict(list)
    for c in viable:
        for d in cand_fixed_diffs[c]:
            type2[d].append(c)

    # Build type-3 index + handle fixed-diff collisions
    type3 = defaultdict(list)
    for i in range(len(viable)):
        c1 = viable[i]
        for j in range(i + 1, len(viable)):
            c2 = viable[j]
            d = abs(c1 - c2)
            if d in fixed_diffs:
                # This diff already used by fixed elements — can't both be selected
                model.add(y[c1] + y[c2] <= 1)
            else:
                type3[d].append((c1, c2))

    # Add unified at-most-one constraints per diff value
    all_diff_values = set(type2.keys()) | set(type3.keys())

    for d in all_diff_values:
        t2 = type2.get(d, [])
        t3 = type3.get(d, [])

        # If total sources <= 1, constraint is auto-satisfied
        if len(t2) + len(t3) <= 1:
            continue

        indicators = []

        # Type-2 indicators: y[c] directly (selecting c activates diff d)
        for c in t2:
            indicators.append(y[c])

        # Type-3 indicators: pair variable p = (y[c1] AND y[c2])
        for c1, c2 in t3:
            p = model.new_bool_var(f"p_{c1}_{c2}_{d}")
            model.add_implication(p, y[c1])
            model.add_implication(p, y[c2])
            model.add_bool_or([p, y[c1].negated(), y[c2].negated()])
            indicators.append(p)

        model.add_at_most_one(indicators)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = num_workers
    status = solver.solve(model)
    elapsed = time.time() - t0

    solution = None
    size = 0
    free_count = 0
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        free_elements = sorted(c for c in candidates if solver.value(y[c]))
        solution = sorted(fixed + free_elements)
        size = len(solution)
        free_count = len(free_elements)

    return {"status": _status_name(status), "solution": solution,
            "size": size, "time_s": round(elapsed, 3),
            "fixed_count": len(fixed), "free_count": free_count}


def vlns_batch(base_set, removal_sizes, n_trials_per_size, N=10000,
               time_limit_per_trial=30, num_workers=8, seed=42):
    """Batch VLNS trials: for each removal size, run multiple random removals.

    For each removal size k, randomly removes k elements from base_set, then
    runs VLNS targeting k+1 free elements (net gain of 1 if successful).

    Args:
        base_set: list[int] — base Sidon set to perturb.
        removal_sizes: list[int] — how many elements to remove per trial.
        n_trials_per_size: int — random trials per removal size.
        N: int — range upper bound. Default 10000.
        time_limit_per_trial: float — time limit per VLNS call. Default 30.
        num_workers: int — workers per trial. Default 8.
        seed: int — random seed. Default 42.

    Returns:
        list of dicts: [{removal_size, trial, removed, n_free, result}, ...]
    """
    rng = random.Random(seed)
    base_sorted = sorted(base_set)
    results = []

    for removal_size in removal_sizes:
        if removal_size >= len(base_sorted):
            continue
        for trial in range(n_trials_per_size):
            removed = sorted(rng.sample(base_sorted, removal_size))
            removed_set = set(removed)
            fixed = [e for e in base_sorted if e not in removed_set]
            n_free = removal_size + 1

            result = vlns_sidon(fixed, n_free, N, time_limit_per_trial, num_workers)
            results.append({
                "removal_size": removal_size,
                "trial": trial,
                "removed": removed,
                "n_free": n_free,
                "result": result,
            })

    return results


def self_test():
    """Run self-tests to verify all functions produce valid Sidon sets.

    Raises AssertionError on failure.
    """
    try:
        from helpers.core import is_sidon
    except ImportError:
        def is_sidon(S):
            S = sorted(set(S))
            sums = set()
            for i in range(len(S)):
                for j in range(i, len(S)):
                    s = S[i] + S[j]
                    if s in sums:
                        return False
                    sums.add(s)
            return True

    print("=" * 60)
    print("CP-SAT Helper Self-Test")
    print("=" * 60)

    # Test 1: solve_sidon_cpsat with small N (binary formulation)
    print("\nTest 1: solve_sidon_cpsat(k=10, N=100, time_limit=30)")
    r1 = solve_sidon_cpsat(k=10, N=100, time_limit=30)
    print(f"  Status: {r1['status']}, Size: {r1['size']}, Time: {r1['time_s']}s")
    if r1['solution']:
        print(f"  Solution: {r1['solution']}")
        assert is_sidon(r1['solution']), "Test 1 FAILED: not a valid Sidon set!"
        assert r1['size'] >= 10, f"Test 1 FAILED: size {r1['size']} < 10"
        assert all(0 <= x <= 100 for x in r1['solution']), "Out of range!"
    print("  PASSED")

    # Test 2: vlns_sidon with small example
    print("\nTest 2: vlns_sidon([0,1,3,7,12,20], n_free=2, N=50, time_limit=10)")
    r2 = vlns_sidon([0, 1, 3, 7, 12, 20], n_free=2, N=50, time_limit=10)
    print(f"  Status: {r2['status']}, Size: {r2['size']}, Fixed: {r2['fixed_count']}, Free: {r2['free_count']}, Time: {r2['time_s']}s")
    if r2['solution']:
        print(f"  Solution: {r2['solution']}")
        valid = is_sidon(r2['solution'])
        print(f"  is_sidon: {valid}")
        assert valid, "Test 2 FAILED: VLNS solution is not a valid Sidon set!"
        for f in [0, 1, 3, 7, 12, 20]:
            assert f in r2['solution'], f"Test 2 FAILED: fixed element {f} missing!"
        assert all(0 <= x <= 50 for x in r2['solution']), "Out of range!"
    else:
        if r2['status'] == 'INFEASIBLE' and r2['time_s'] < 1.0:
            raise AssertionError("Test 2 FAILED: sub-1s INFEASIBLE suggests formulation bug")
        print(f"  No solution ({r2['status']}), but not sub-1s INFEASIBLE (OK)")
    print("  PASSED")

    # Test 3: vlns with larger base set
    print("\nTest 3: vlns_sidon with 6-element fixed, n_free=2, N=200")
    base = [0, 1, 3, 7, 12, 20, 30, 44]
    assert is_sidon(base), "Base not Sidon!"
    r3 = vlns_sidon(base[:6], n_free=2, N=200, time_limit=15)
    print(f"  Status: {r3['status']}, Size: {r3['size']}, Time: {r3['time_s']}s")
    if r3['solution']:
        print(f"  Solution: {r3['solution']}")
        valid = is_sidon(r3['solution'])
        print(f"  is_sidon: {valid}")
        assert valid, "Test 3 FAILED: not Sidon!"
    if r3['status'] == 'INFEASIBLE' and r3['time_s'] < 1.0:
        raise AssertionError("Test 3 FAILED: sub-1s INFEASIBLE")
    print("  PASSED")

    # Test 4: vlns_batch
    print("\nTest 4: vlns_batch([0,1,3,7,12,20,30,44], [2], 2, N=100)")
    base4 = [0, 1, 3, 7, 12, 20, 30, 44]
    assert is_sidon(base4), "Base not Sidon!"
    r4 = vlns_batch(base4, [2], 2, N=100, time_limit_per_trial=10)
    print(f"  Trials: {len(r4)}")
    for trial in r4:
        res = trial['result']
        print(f"    rm={trial['removal_size']}, trial={trial['trial']}, "
              f"status={res['status']}, size={res['size']}")
        if res['solution']:
            assert is_sidon(res['solution']), f"Test 4 FAILED: trial {trial['trial']} not Sidon!"
    print("  PASSED")

    # Test 5: Regression — free-to-free vs free-to-fixed diff collision
    print("\nTest 5: Regression — free-to-free vs free-to-fixed diff collision")
    r5 = vlns_sidon([0, 1, 3, 7, 12, 20], n_free=3, N=50, time_limit=10)
    print(f"  Status: {r5['status']}, Size: {r5['size']}, Time: {r5['time_s']}s")
    if r5['solution']:
        print(f"  Solution: {r5['solution']}")
        valid = is_sidon(r5['solution'])
        print(f"  is_sidon: {valid}")
        assert valid, "Test 5 FAILED: solution not Sidon!"
    print("  PASSED")

    # Test 6: solve_sidon_cpsat with element formulation (N > 500)
    print("\nTest 6: solve_sidon_cpsat(k=10, N=1000, time_limit=30)")
    r6 = solve_sidon_cpsat(k=10, N=1000, time_limit=30)
    print(f"  Status: {r6['status']}, Size: {r6['size']}, Time: {r6['time_s']}s")
    if r6['solution']:
        print(f"  Solution: {r6['solution']}")
        assert is_sidon(r6['solution']), "Test 6 FAILED: not Sidon!"
        assert r6['size'] >= 10, f"Test 6 FAILED: size {r6['size']} < 10"
        assert all(0 <= x <= 1000 for x in r6['solution']), "Out of range!"
    print("  PASSED")

    print("\n" + "=" * 60)
    print("ALL SELF-TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    self_test()
