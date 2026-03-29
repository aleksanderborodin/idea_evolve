"""Tests for cross_convolution_f64.py."""

import sys
import numpy as np

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/workspace/gen007_experimentator_1/output')
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

from helpers.cross_convolution_f64 import cross_convolve, autoconvolve, tight_constraint_indices


def test_cross_convolve_vs_numpy(N=500):
    """cross_convolve(f, g) should match numpy's np.convolve(f, g) * dx."""
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(N)) * 0.1
    g = np.abs(rng.standard_normal(N)) * 0.1
    dx = 0.5 / N

    result = cross_convolve(f, g, dx=dx)

    # np.convolve gives the unscaled convolution sum
    ref = np.convolve(f, g) * dx  # length 2N-1

    max_err = np.max(np.abs(result - ref))
    return max_err


def test_autoconvolve_vs_compute_c_f64(N=500):
    """autoconvolve(f) max / integral^2 should match compute_c_f64(f)."""
    from helpers.compute_c_f64 import compute_c_f64

    rng = np.random.default_rng(77)
    f = np.abs(rng.standard_normal(N)) * 0.1

    autoconv, f_padded, dx, M = autoconvolve(f)
    max_conv = np.max(autoconv)
    integral = np.sum(np.maximum(f, 0.0)) * dx
    c_from_autoconv = max_conv / integral**2

    c_reference = compute_c_f64(f)

    err = abs(c_from_autoconv - c_reference)
    return err


def test_autoconvolve_length(N=500):
    """autoconvolve should return array of length 2N."""
    f = np.ones(N) * 0.1
    autoconv, f_padded, dx, M = autoconvolve(f)
    assert len(autoconv) == 2 * N, f"Expected {2*N}, got {len(autoconv)}"
    assert len(f_padded) == 2 * N, f"Expected {2*N}, got {len(f_padded)}"
    assert M == 2 * N
    return True


def test_cross_convolve_length(N=500):
    """cross_convolve should return array of length 2N-1."""
    f = np.ones(N) * 0.1
    g = np.ones(N) * 0.2
    result = cross_convolve(f, g)
    assert len(result) == 2 * N - 1, f"Expected {2*N-1}, got {len(result)}"
    return True


def test_autoconvolve_vs_incremental(N=500):
    """autoconvolve output should be compatible with incremental_update."""
    sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/workspace/gen007_experimentator_1/output')
    from helpers.incremental_autoconv_update import incremental_update

    rng = np.random.default_rng(99)
    f = np.abs(rng.standard_normal(N)) * 0.1

    # Get autoconv and f_padded from autoconvolve
    autoconv, f_padded, dx, M = autoconvolve(f)

    # Apply incremental update
    idx = 100
    delta = 0.01
    new_autoconv = incremental_update(autoconv, f_padded, idx, delta, dx, M)

    # Reference: recompute with updated f
    f_ref = f.copy()
    f_ref[idx] += delta
    autoconv_ref, _, _, _ = autoconvolve(f_ref)

    max_err = np.max(np.abs(new_autoconv - autoconv_ref))
    return max_err


def test_constant_function_autoconv():
    """For constant f=c on [0, N], autoconvolution is a triangle function."""
    N = 1000
    c_val = 0.1
    f = np.ones(N) * c_val
    dx = 0.5 / N

    ac = cross_convolve(f, f, dx=dx)

    # For f=c, (f★f)(n) = sum_{k=0}^{N-1} c*c*dx * [n-k in [0,N-1]]
    # At n=N-1 (peak): all N terms contribute, so peak = N * c^2 * dx = N*c^2*(0.5/N) = 0.5*c^2
    expected_peak = 0.5 * c_val**2
    actual_peak = np.max(ac)

    err = abs(actual_peak - expected_peak)
    return err


def test_tight_constraint_constant():
    """For constant function, autoconv is peaked at exactly one index."""
    N = 1000
    f = np.ones(N) * 0.1

    idx = tight_constraint_indices(f, epsilon_rel=1e-10)

    # Constant function: the triangle autoconvolution peaks at index N-1
    # (where both sequences align perfectly)
    assert len(idx) == 1, f"Expected 1 tight index, got {len(idx)}: {idx}"
    assert idx[0] == N - 1, f"Expected peak at {N-1}, got {idx[0]}"
    return True


def test_tight_constraint_monotone(N=500):
    """More constraints at larger epsilon_rel."""
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(N)) * 0.1

    n_tight_small = len(tight_constraint_indices(f, epsilon_rel=1e-8))
    n_tight_medium = len(tight_constraint_indices(f, epsilon_rel=1e-5))
    n_tight_large = len(tight_constraint_indices(f, epsilon_rel=1e-3))

    assert n_tight_small <= n_tight_medium <= n_tight_large, \
        f"Non-monotone: {n_tight_small} <= {n_tight_medium} <= {n_tight_large}"
    return n_tight_small, n_tight_medium, n_tight_large


def test_dx_default_convention(N=500):
    """Default dx=0.5/N should match standard problem convention."""
    rng = np.random.default_rng(55)
    f = np.abs(rng.standard_normal(N)) * 0.1
    dx = 0.5 / N

    # Explicit dx should match implicit dx
    result_explicit = cross_convolve(f, f, dx=dx)
    result_implicit = cross_convolve(f, f)

    max_err = np.max(np.abs(result_explicit - result_implicit))
    assert max_err == 0.0, f"Default dx mismatch: {max_err}"
    return True


if __name__ == '__main__':
    all_passed = True

    print("=" * 60)
    print("Tests for cross_convolution_f64.py")
    print("=" * 60)

    # Test 1: cross_convolve vs numpy reference
    print("\n--- cross_convolve vs np.convolve (N=500) ---")
    err = test_cross_convolve_vs_numpy(N=500)
    status = "PASS" if err < 1e-14 else "FAIL"
    print(f"  max_err={err:.3e} — {status}")
    if err >= 1e-14:
        all_passed = False

    # Test 2: autoconvolve vs compute_c_f64
    print("\n--- autoconvolve max/integral^2 vs compute_c_f64 ---")
    err = test_autoconvolve_vs_compute_c_f64()
    status = "PASS" if err < 1e-12 else "FAIL"
    print(f"  |c_autoconvolve - c_reference|={err:.3e} — {status}")
    if err >= 1e-12:
        all_passed = False

    # Test 3: length of autoconvolve output
    print("\n--- autoconvolve output length = 2N ---")
    ok = test_autoconvolve_length()
    print(f"  {'PASS' if ok else 'FAIL'}")
    if not ok:
        all_passed = False

    # Test 4: length of cross_convolve output
    print("\n--- cross_convolve output length = 2N-1 ---")
    ok = test_cross_convolve_length()
    print(f"  {'PASS' if ok else 'FAIL'}")
    if not ok:
        all_passed = False

    # Test 5: compatibility with incremental_update
    print("\n--- autoconvolve output compatible with incremental_update ---")
    err = test_autoconvolve_vs_incremental()
    status = "PASS" if err < 1e-14 else "FAIL"
    print(f"  max_err={err:.3e} — {status}")
    if err >= 1e-14:
        all_passed = False

    # Test 6: constant function analytical check
    print("\n--- Constant function peak value (analytical) ---")
    err = test_constant_function_autoconv()
    status = "PASS" if err < 1e-12 else "FAIL"
    print(f"  |peak - expected|={err:.3e} — {status}")
    if err >= 1e-12:
        all_passed = False

    # Test 7: tight_constraint_indices on constant function
    print("\n--- tight_constraint_indices: constant function peak ---")
    try:
        ok = test_tight_constraint_constant()
        print(f"  Peak index and count: PASS")
    except AssertionError as e:
        print(f"  FAIL: {e}")
        all_passed = False

    # Test 8: tight constraint monotonicity
    print("\n--- tight_constraint_indices: monotone in epsilon_rel ---")
    try:
        n_s, n_m, n_l = test_tight_constraint_monotone()
        print(f"  n_tight(1e-8)={n_s}, n_tight(1e-5)={n_m}, n_tight(1e-3)={n_l} — PASS")
    except AssertionError as e:
        print(f"  FAIL: {e}")
        all_passed = False

    # Test 9: default dx convention
    print("\n--- Default dx convention ---")
    try:
        test_dx_default_convention()
        print("  PASS")
    except AssertionError as e:
        print(f"  FAIL: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)
