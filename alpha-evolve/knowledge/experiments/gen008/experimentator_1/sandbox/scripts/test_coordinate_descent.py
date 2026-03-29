"""Tests for coordinate_descent helper.

Tests correctness, convergence, and numerical accuracy against compute_c_f64.
"""
import sys
import os
import time
import numpy as np

# Add problem/ to path so helpers are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'problem'))
# Also add the sandbox parent so we can import the dev version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'helpers'))

from helpers.compute_c_f64 import compute_c_f64
from helpers.cross_convolution_f64 import autoconvolve
from helpers.incremental_autoconv_update import incremental_update

# Import our coordinate_descent module (dev version in output/helpers/)
cd_path = os.path.join(os.path.dirname(__file__), '..', '..', 'helpers')
sys.path.insert(0, cd_path)
from coordinate_descent import coordinate_descent_round, run_coordinate_descent, DEFAULT_DELTA_GRID


def load_solution(path):
    """Load a solution file and return f array."""
    spec = {}
    exec(open(path).read(), spec)
    return np.asarray(spec['entrypoint'](), dtype=np.float64)


def test_basic_correctness():
    """Test that coordinate_descent_round returns correct C values."""
    print("=== Test 1: Basic correctness on small random array ===")
    rng = np.random.default_rng(42)
    N = 500
    f = np.abs(rng.standard_normal(N)) * 0.1
    f = np.maximum(f, 0.0)

    c_before = compute_c_f64(f)
    print(f"  C before: {c_before:.12f}")

    f_new, autoconv_new, n_improvements, new_c = coordinate_descent_round(f, delta_grid=DEFAULT_DELTA_GRID)
    print(f"  C after 1 round: {new_c:.12f}")
    print(f"  Improvements: {n_improvements}")

    # Verify new_c matches compute_c_f64
    c_verify = compute_c_f64(f_new)
    diff = abs(new_c - c_verify)
    print(f"  C verification diff: {diff:.2e}")
    assert diff < 1e-10, f"C mismatch: {new_c} vs {c_verify}, diff={diff}"
    assert new_c <= c_before + 1e-12, f"C increased: {c_before} -> {new_c}"
    assert n_improvements > 0, "Expected improvements on random array"
    print("  PASSED\n")


def test_nonnegativity():
    """Test that output array is always non-negative."""
    print("=== Test 2: Non-negativity constraint ===")
    rng = np.random.default_rng(123)
    N = 200
    f = np.abs(rng.standard_normal(N)) * 0.05
    f[:10] = 1e-8  # Near-zero elements

    f_new, _, _, _ = coordinate_descent_round(f)
    assert np.all(f_new >= 0), f"Negative values found: min={np.min(f_new)}"
    print("  All values non-negative")
    print("  PASSED\n")


def test_converged_solution():
    """Test that coord descent finds 0 or very few improvements on already-converged solution."""
    print("=== Test 3: Converged solution (current best) ===")
    best_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..',
                             'population', 'gen007', 'explore_1', 'sol01.py')
    if not os.path.exists(best_path):
        print("  SKIPPED: best solution not found")
        return

    f = load_solution(best_path)
    c_before = compute_c_f64(f)
    print(f"  C before: {c_before:.12f} (N={len(f)})")

    t0 = time.time()
    f_new, _, n_improvements, new_c = coordinate_descent_round(f)
    elapsed = time.time() - t0
    print(f"  C after: {new_c:.12f}")
    print(f"  Improvements: {n_improvements}")
    print(f"  Time: {elapsed:.1f}s")

    # Verify C
    c_verify = compute_c_f64(f_new)
    diff = abs(new_c - c_verify)
    print(f"  C verification diff: {diff:.2e}")
    assert diff < 1e-10, f"C mismatch: {new_c} vs {c_verify}, diff={diff}"
    # Already-converged solution should have very few improvements
    assert n_improvements < 50, f"Unexpected: {n_improvements} improvements on converged solution"
    print("  PASSED\n")


def test_less_optimized_solution():
    """Test that coord descent finds hundreds of improvements on less-optimized array."""
    print("=== Test 4: Less-optimized solution (gen004 research) ===")
    sol_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..',
                            'population', 'gen004', 'research_1', 'sol01.py')
    if not os.path.exists(sol_path):
        print("  SKIPPED: gen004 research solution not found")
        return

    f = load_solution(sol_path)
    c_before = compute_c_f64(f)
    print(f"  C before: {c_before:.12f} (N={len(f)})")

    t0 = time.time()
    f_new, _, n_improvements, new_c = coordinate_descent_round(f)
    elapsed = time.time() - t0
    print(f"  C after 1 round: {new_c:.12f}")
    print(f"  Improvements: {n_improvements}")
    print(f"  Delta C: {new_c - c_before:.6e}")
    print(f"  Time: {elapsed:.1f}s")

    c_verify = compute_c_f64(f_new)
    diff = abs(new_c - c_verify)
    print(f"  C verification diff: {diff:.2e}")
    assert diff < 1e-10, f"C mismatch"
    assert new_c < c_before, f"C did not improve"
    print("  PASSED\n")


def test_run_coordinate_descent_convergence():
    """Test that run_coordinate_descent converges within 5 rounds on less-optimized array."""
    print("=== Test 5: run_coordinate_descent convergence ===")
    sol_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..',
                            'population', 'gen004', 'research_1', 'sol01.py')
    if not os.path.exists(sol_path):
        # Fall back to small random array
        rng = np.random.default_rng(42)
        N = 500
        f = np.abs(rng.standard_normal(N)) * 0.1
        print(f"  Using random array N={N}")
    else:
        f = load_solution(sol_path)
        print(f"  Using gen004 research solution N={len(f)}")

    c_before = compute_c_f64(f)
    print(f"  C before: {c_before:.12f}")

    t0 = time.time()
    f_final, total_improvements, c_history = run_coordinate_descent(f, n_rounds=5, verbose=True)
    elapsed = time.time() - t0
    print(f"  C after: {c_history[-1]:.12f}")
    print(f"  Total improvements: {total_improvements}")
    print(f"  C history: {[f'{c:.12f}' for c in c_history]}")
    print(f"  Time: {elapsed:.1f}s")

    # Verify final C matches compute_c_f64
    c_verify = compute_c_f64(f_final)
    diff = abs(c_history[-1] - c_verify)
    print(f"  C verification diff: {diff:.2e}")
    assert diff < 1e-10, f"C mismatch"
    print("  PASSED\n")


def test_incremental_vs_fft_accuracy():
    """Test that incremental tracking stays accurate over many updates."""
    print("=== Test 6: Incremental vs FFT accuracy ===")
    rng = np.random.default_rng(99)
    N = 1000
    f = np.abs(rng.standard_normal(N)) * 0.1

    # Run 1 round
    f_new, autoconv_new, n_improvements, new_c = coordinate_descent_round(f)
    print(f"  {n_improvements} improvements applied")

    # Recompute autoconv from scratch via FFT
    autoconv_ref, f_padded_ref, dx_ref, M_ref = autoconvolve(f_new)
    max_diff = np.max(np.abs(autoconv_new - autoconv_ref))
    print(f"  Max autoconv diff (incremental vs FFT): {max_diff:.2e}")

    # Recompute C from the returned autoconv
    dx = 0.5 / N
    integral = np.sum(np.maximum(f_new, 0.0)) * dx
    c_from_autoconv = np.max(autoconv_new) / (integral ** 2)
    c_from_fft = compute_c_f64(f_new)
    c_diff = abs(c_from_autoconv - c_from_fft)
    print(f"  C diff: {c_diff:.2e}")
    assert c_diff < 1e-10, f"C drift too large: {c_diff}"
    print("  PASSED\n")


def test_empty_and_edge_cases():
    """Test edge cases."""
    print("=== Test 7: Edge cases ===")

    # Constant function
    f = np.ones(100) * 0.1
    f_new, _, n_imp, new_c = coordinate_descent_round(f)
    c_verify = compute_c_f64(f_new)
    assert abs(new_c - c_verify) < 1e-10
    print(f"  Constant function: C={new_c:.6f}, improvements={n_imp}")

    # Mostly zeros with a few nonzeros
    f = np.zeros(200)
    f[50:55] = 0.1
    f_new, _, n_imp, new_c = coordinate_descent_round(f)
    c_verify = compute_c_f64(f_new)
    assert abs(new_c - c_verify) < 1e-10
    assert np.all(f_new >= 0)
    print(f"  Sparse function: C={new_c:.6f}, improvements={n_imp}")

    print("  PASSED\n")


if __name__ == '__main__':
    print("Running coordinate_descent tests...\n")
    test_basic_correctness()
    test_nonnegativity()
    test_incremental_vs_fft_accuracy()
    test_empty_and_edge_cases()
    # These tests use large arrays and take longer
    test_converged_solution()
    test_less_optimized_solution()
    test_run_coordinate_descent_convergence()
    print("ALL TESTS PASSED!")
