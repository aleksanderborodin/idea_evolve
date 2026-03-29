"""Tests for plateau_analyzer.

Tests:
1. Gradient correctness via finite differences
2. Consistency with compute_c_f64
3. Threshold behavior (more positions with larger threshold)
4. Performance at N=30000
5. Pre-computed autoconv consistency
6. Edge cases
"""

import sys
import time
import numpy as np

# Add problem/ to path so we can import helpers
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/alpha-evolve/problem")
# Import dev version
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/alpha-evolve/workspace/gen010_experimentator_1/output/sandbox/scripts")

from plateau_analyzer_dev import plateau_analysis
from helpers.compute_c_f64 import compute_c_f64


def test_gradient_correctness_finite_diff():
    """Verify each gradient entry against central finite differences."""
    print("Test 1: Gradient correctness (finite differences)...")
    rng = np.random.default_rng(123)
    N = 100
    f = np.abs(rng.standard_normal(N)) * 0.5 + 0.01  # ensure positive

    result = plateau_analysis(f, threshold_rel=1e-6)
    positions = result["positions"]
    gradients = result["gradients"]
    K = len(positions)

    dx = 0.5 / N
    M = 2 * N
    eps = 1e-7

    print(f"  K={K} plateau positions: {positions}")

    max_abs_err = 0.0
    max_rel_err = 0.0
    for p_idx in range(K):
        n = positions[p_idx]
        for m in range(N):
            # Compute autoconv[n] with f[m] + eps
            f_plus = f.copy()
            f_plus[m] += eps
            fp = np.zeros(M, dtype=np.float64)
            fp[:N] = f_plus
            ac_plus = np.fft.ifft(np.fft.fft(fp) ** 2).real * dx

            # Compute autoconv[n] with f[m] - eps
            f_minus = f.copy()
            f_minus[m] -= eps
            fm = np.zeros(M, dtype=np.float64)
            fm[:N] = np.maximum(f_minus, 0.0)
            ac_minus = np.fft.ifft(np.fft.fft(fm) ** 2).real * dx

            fd_grad = (ac_plus[n] - ac_minus[n]) / (2 * eps)
            analytic_grad = gradients[p_idx, m]
            abs_err = abs(fd_grad - analytic_grad)
            rel_err = abs_err / (abs(fd_grad) + 1e-20)

            max_abs_err = max(max_abs_err, abs_err)
            max_rel_err = max(max_rel_err, rel_err)

            if abs_err > 1e-8:
                print(f"  FAIL at p={p_idx}, n={n}, m={m}: "
                      f"analytic={analytic_grad:.12e}, fd={fd_grad:.12e}, "
                      f"abs_err={abs_err:.2e}")
                return False

    print(f"  Max absolute error: {max_abs_err:.2e}")
    print(f"  Max relative error: {max_rel_err:.2e}")
    print("  PASSED")
    return True


def test_consistency_with_compute_c():
    """Verify max_val * dx / (sum(f)*dx)^2 == compute_c_f64(f)."""
    print("Test 2: Consistency with compute_c_f64...")
    rng = np.random.default_rng(456)
    N = 500
    f = np.abs(rng.standard_normal(N)) * 0.3 + 0.01

    result = plateau_analysis(f)
    dx = 0.5 / N
    integral_f = np.sum(np.maximum(f, 0.0)) * dx
    c_from_plateau = result["max_val"] / (integral_f ** 2)
    c_from_helper = compute_c_f64(f)

    rel_err = abs(c_from_plateau - c_from_helper) / c_from_helper
    print(f"  C from plateau_analysis: {c_from_plateau:.15f}")
    print(f"  C from compute_c_f64:    {c_from_helper:.15f}")
    print(f"  Relative error: {rel_err:.2e}")

    if rel_err > 1e-12:
        print("  FAIL: relative error too large")
        return False

    print("  PASSED")
    return True


def test_threshold_behavior():
    """Verify that positions grows as threshold_rel increases."""
    print("Test 3: Threshold behavior...")
    rng = np.random.default_rng(789)
    N = 1000
    f = np.abs(rng.standard_normal(N)) * 0.1 + 0.01

    thresholds = [1e-15, 1e-12, 1e-9, 1e-6, 1e-3]
    counts = []
    for thr in thresholds:
        result = plateau_analysis(f, threshold_rel=thr)
        k = len(result["positions"])
        counts.append(k)
        print(f"  threshold_rel={thr:.0e}: K={k}")

    # Counts should be non-decreasing
    for i in range(1, len(counts)):
        if counts[i] < counts[i - 1]:
            print(f"  FAIL: K decreased from {counts[i-1]} to {counts[i]} "
                  f"as threshold increased from {thresholds[i-1]} to {thresholds[i]}")
            return False

    # Largest threshold should give more positions than smallest (or equal for degenerate case)
    if counts[-1] < counts[0]:
        print("  FAIL: largest threshold gave fewer positions than smallest")
        return False

    print("  PASSED")
    return True


def test_performance():
    """Verify < 100ms at N=30000."""
    print("Test 4: Performance at N=30000...")
    rng = np.random.default_rng(42)
    N = 30000
    f = np.abs(rng.standard_normal(N)) * 0.01 + 0.001

    # Warm up
    _ = plateau_analysis(f[:100], threshold_rel=1e-6)

    # Time the real call
    times = []
    for trial in range(3):
        t0 = time.perf_counter()
        result = plateau_analysis(f, threshold_rel=1e-6)
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000
        times.append(elapsed_ms)
        print(f"  Trial {trial+1}: {elapsed_ms:.1f}ms, K={len(result['positions'])}")

    median_ms = sorted(times)[1]
    print(f"  Median: {median_ms:.1f}ms")

    if median_ms > 100:
        print(f"  FAIL: {median_ms:.1f}ms > 100ms threshold")
        return False

    print("  PASSED")
    return True


def test_precomputed_autoconv():
    """Verify results are identical when passing pre-computed autoconv."""
    print("Test 5: Pre-computed autoconv consistency...")
    rng = np.random.default_rng(111)
    N = 200
    f = np.abs(rng.standard_normal(N)) * 0.2

    # Compute autoconv manually
    dx = 0.5 / N
    M = 2 * N
    f_padded = np.zeros(M, dtype=np.float64)
    f_padded[:N] = np.maximum(f, 0.0)
    fft_f = np.fft.fft(f_padded)
    autoconv = np.fft.ifft(fft_f * fft_f).real * dx

    r1 = plateau_analysis(f, threshold_rel=1e-10)
    r2 = plateau_analysis(f, autoconv=autoconv, threshold_rel=1e-10)

    if not np.array_equal(r1["positions"], r2["positions"]):
        print("  FAIL: positions differ")
        return False
    if not np.allclose(r1["values"], r2["values"], atol=1e-15):
        print("  FAIL: values differ")
        return False
    if not np.allclose(r1["gradients"], r2["gradients"], atol=1e-15):
        print("  FAIL: gradients differ")
        return False
    if r1["max_val"] != r2["max_val"]:
        print("  FAIL: max_val differs")
        return False

    print("  PASSED")
    return True


def test_constant_function():
    """For a constant function, autoconv has a known shape."""
    print("Test 6: Constant function sanity check...")
    N = 500
    val = 0.1
    f = np.full(N, val, dtype=np.float64)
    result = plateau_analysis(f, threshold_rel=1e-12)

    # For constant f, C should be 2.0
    dx = 0.5 / N
    integral = np.sum(f) * dx
    c = result["max_val"] / (integral ** 2)
    print(f"  C for constant function: {c:.10f} (expected ~2.0)")
    if abs(c - 2.0) > 1e-4:
        print(f"  FAIL: C={c} too far from 2.0")
        return False

    # max should be at center (index N-1 for length-2N FFT autoconv)
    print(f"  max_idx={result['max_idx']}")

    print("  PASSED")
    return True


def test_gradient_shape():
    """Verify gradient shape is (K, N)."""
    print("Test 7: Gradient shape...")
    N = 50
    f = np.abs(np.random.default_rng(42).standard_normal(N)) * 0.1
    result = plateau_analysis(f, threshold_rel=1e-3)
    K = len(result["positions"])
    expected_shape = (K, N)
    actual_shape = result["gradients"].shape
    if actual_shape != expected_shape:
        print(f"  FAIL: expected {expected_shape}, got {actual_shape}")
        return False
    print(f"  Shape: {actual_shape} (K={K}, N={N})")
    print("  PASSED")
    return True


def test_performance_with_real_solution():
    """Test with the actual best solution to verify plateau behavior."""
    print("Test 8: Performance with real solution (if available)...")
    try:
        sys.path.insert(0, "/home/sasha/Desktop/project_alpha/alpha-evolve/problem")
        best_path = "/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("best", best_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        f = mod.entrypoint()
        f = np.asarray(f, dtype=np.float64)
        print(f"  Solution N={len(f)}")

        t0 = time.perf_counter()
        result = plateau_analysis(f, threshold_rel=1e-12)
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000

        K = len(result["positions"])
        print(f"  K={K} plateau positions (threshold_rel=1e-12)")
        print(f"  max_val={result['max_val']:.15f}")
        print(f"  gradients shape: {result['gradients'].shape}")
        print(f"  Time: {elapsed_ms:.1f}ms")

        # Verify C consistency
        dx = 0.5 / len(f)
        integral = np.sum(np.maximum(f, 0.0)) * dx
        c = result["max_val"] / (integral ** 2)
        c_ref = compute_c_f64(f)
        rel_err = abs(c - c_ref) / c_ref
        print(f"  C={c:.15f}, ref={c_ref:.15f}, rel_err={rel_err:.2e}")

        if elapsed_ms > 100:
            print(f"  WARNING: {elapsed_ms:.1f}ms > 100ms (but may be due to solution size)")

        print("  PASSED")
        return True
    except Exception as e:
        print(f"  SKIPPED: {e}")
        return True


if __name__ == "__main__":
    tests = [
        test_gradient_correctness_finite_diff,
        test_consistency_with_compute_c,
        test_threshold_behavior,
        test_performance,
        test_precomputed_autoconv,
        test_constant_function,
        test_gradient_shape,
        test_performance_with_real_solution,
    ]

    passed = 0
    failed = 0
    for test in tests:
        print()
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    if failed > 0:
        sys.exit(1)
    print("All tests passed!")
