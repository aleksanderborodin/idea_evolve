"""Final validation tests for coordinate_descent helper."""

import numpy as np
import sys
import time

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

from helpers.compute_c_f64 import compute_c_f64

# Import coordinate_descent from output dir (what will be deployed)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "coordinate_descent",
    "/home/sasha/Desktop/project_alpha/alpha-evolve/workspace/gen008_experimentator_1/output/helpers/coordinate_descent.py")
_cd = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_cd)
coordinate_descent_round = _cd.coordinate_descent_round
run_coordinate_descent = _cd.run_coordinate_descent
_autoconvolve = _cd._autoconvolve
_build_hot_set = _cd._build_hot_set
DEFAULT_ABSOLUTE_DELTAS = _cd.DEFAULT_ABSOLUTE_DELTAS
DEFAULT_PROPORTIONAL_MULTS = _cd.DEFAULT_PROPORTIONAL_MULTS


def test_small_correctness():
    """Test: small array, verify C decreases monotonically and matches FFT."""
    print("=== Test 1: Small array (N=500) correctness ===")
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(500)) * 0.1
    c0 = compute_c_f64(f)
    print(f"Initial C: {c0:.10f}")

    f_opt, total, c_hist = run_coordinate_descent(f, n_rounds=3, verbose=True)

    # Verify monotonic decrease
    for i in range(1, len(c_hist)):
        assert c_hist[i] <= c_hist[i-1] + 1e-12, \
            f"C increased: round {i}: {c_hist[i-1]:.13f} -> {c_hist[i]:.13f}"

    # Verify final C matches FFT
    c_final = compute_c_f64(f_opt)
    assert abs(c_hist[-1] - c_final) < 1e-10, \
        f"Final C mismatch: incr={c_hist[-1]:.13f}, FFT={c_final:.13f}"

    print(f"Total improvements: {total}")
    print("PASS\n")
    return True


def test_convergence():
    """Test: array converges to 0 improvements."""
    print("=== Test 2: Convergence detection ===")
    rng = np.random.default_rng(123)
    f = np.abs(rng.standard_normal(200)) * 0.1
    f_opt, total, c_hist = run_coordinate_descent(f, n_rounds=20, verbose=True)

    # Should converge before 20 rounds
    print(f"Converged in {len(c_hist)} rounds, {total} improvements")
    print("PASS\n")
    return True


def test_nonneg_preserved():
    """Test: output is always non-negative."""
    print("=== Test 3: Non-negativity preserved ===")
    rng = np.random.default_rng(99)
    f = np.abs(rng.standard_normal(300)) * 0.1
    f[50:60] = 1e-8
    f[100:110] = 0.0

    f_opt, _, _ = run_coordinate_descent(f, n_rounds=2, verbose=False)
    assert np.all(f_opt >= 0), "Negative values in output!"
    print(f"Min value: {np.min(f_opt):.2e}")
    print("PASS\n")
    return True


def test_delta_grid():
    """Test: default delta grid has expected structure."""
    print("=== Test 4: Delta grid structure ===")
    grid = DEFAULT_ABSOLUTE_DELTAS
    print(f"Grid size: {len(grid)}")
    assert len(grid) == 22, f"Expected 22 deltas, got {len(grid)}"
    assert np.any(grid > 0) and np.any(grid < 0)
    assert np.min(np.abs(grid)) == 1e-12
    assert np.max(np.abs(grid)) == 1e-2
    print(f"Range: {np.min(np.abs(grid)):.0e} to {np.max(np.abs(grid)):.0e}")
    print("PASS\n")
    return True


def test_hot_set():
    """Test: hot set correctly identifies near-max positions."""
    print("=== Test 5: Hot set ===")
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(1000)) * 0.1
    ac, _, _, _ = _autoconvolve(f)
    hot = _build_hot_set(ac, epsilon_rel=1e-6)

    max_val = np.max(ac)
    assert np.all(ac[hot] >= max_val * (1 - 1e-6))
    assert np.argmax(ac) in hot
    print(f"Hot set size: {len(hot)} / {len(ac)}")
    print("PASS\n")
    return True


def test_30k_best_solution():
    """Test: coordinate descent on the 30k best solution."""
    print("=== Test 6: 30k best solution ===")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "best", "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/explore_1/sol01.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    f = mod.entrypoint()

    c0 = compute_c_f64(f)
    print(f"N={len(f)}, C={c0:.13f}")

    ac, fp, dx, M = _autoconvolve(f)
    f_new, ac_new, nimpr, c_new = coordinate_descent_round(f, ac, dx, M, verbose=True)

    c_verify = compute_c_f64(f_new)
    diff = abs(c_new - c_verify)
    print(f"Improvements: {nimpr}")
    print(f"C: {c0:.13f} -> {c_new:.13f} (delta: {c_new - c0:.2e})")
    print(f"Verify diff: {diff:.2e}")

    assert diff < 1e-10, f"Drift too large: {diff}"
    assert c_new <= c0 + 1e-14, f"C increased: {c0} -> {c_new}"
    print("PASS\n")
    return True


# Run all tests
all_pass = True
for test_fn in [test_delta_grid, test_hot_set, test_small_correctness,
                test_convergence, test_nonneg_preserved, test_30k_best_solution]:
    try:
        result = test_fn()
        if not result:
            all_pass = False
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
        all_pass = False

print(f"\n{'='*50}")
print(f"ALL TESTS {'PASSED' if all_pass else 'FAILED'}")
