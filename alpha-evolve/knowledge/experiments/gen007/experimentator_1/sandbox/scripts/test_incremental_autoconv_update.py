"""Tests for incremental_autoconv_update.py.

Validates that incremental_update produces results matching full FFT
recomputation to within 1e-14 absolute error.
"""

import sys
import numpy as np

# Add helpers output dir to path
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/workspace/gen007_experimentator_1/output')

from helpers.incremental_autoconv_update import incremental_update, batch_incremental_updates


def make_autoconv(f):
    """Compute autoconvolution the reference way (full FFT)."""
    N = len(f)
    dx = 0.5 / N
    M = 2 * N
    f_padded = np.pad(np.maximum(f, 0.0), (0, N)).astype(np.float64)
    fft_f = np.fft.fft(f_padded)
    autoconv = np.fft.ifft(fft_f * fft_f).real * dx
    return autoconv, f_padded, dx, M


def test_single_perturbation(seed, N=500):
    """Test one random perturbation against full FFT recomputation."""
    rng = np.random.default_rng(seed)
    f = np.abs(rng.standard_normal(N)) * 0.1
    autoconv, f_padded, dx, M = make_autoconv(f)

    # Random perturbation
    idx = int(rng.integers(0, N))
    # Delta can be positive or negative (but f[idx] + delta must stay >= 0)
    delta = rng.uniform(-f[idx] * 0.5, 0.1)

    # Incremental update
    new_autoconv = incremental_update(autoconv, f_padded, idx, delta, dx, M)

    # Reference: update f_padded and recompute full FFT
    f_ref = f.copy()
    f_ref[idx] += delta
    autoconv_ref, _, _, _ = make_autoconv(f_ref)

    max_err = np.max(np.abs(new_autoconv - autoconv_ref))
    return max_err, idx, delta


def test_small_delta(N=1000):
    """Test with very small delta (near machine epsilon)."""
    rng = np.random.default_rng(99)
    f = np.abs(rng.standard_normal(N)) * 0.1
    autoconv, f_padded, dx, M = make_autoconv(f)

    idx = 42
    delta = 1e-12  # tiny delta

    new_autoconv = incremental_update(autoconv, f_padded, idx, delta, dx, M)

    f_ref = f.copy()
    f_ref[idx] += delta
    autoconv_ref, _, _, _ = make_autoconv(f_ref)

    max_err = np.max(np.abs(new_autoconv - autoconv_ref))
    return max_err


def test_large_delta(N=500):
    """Test with large delta (comparable to f values)."""
    rng = np.random.default_rng(77)
    f = np.abs(rng.standard_normal(N)) * 0.1
    autoconv, f_padded, dx, M = make_autoconv(f)

    idx = 200
    delta = 1.0  # large delta

    new_autoconv = incremental_update(autoconv, f_padded, idx, delta, dx, M)

    f_ref = f.copy()
    f_ref[idx] += delta
    autoconv_ref, _, _, _ = make_autoconv(f_ref)

    max_err = np.max(np.abs(new_autoconv - autoconv_ref))
    return max_err


def test_zero_element_perturbation(N=500):
    """Test perturbing an element that was exactly zero."""
    f = np.zeros(N)
    f[100] = 0.5
    f[200] = 0.3
    autoconv, f_padded, dx, M = make_autoconv(f)

    idx = 0  # was zero
    delta = 0.1

    new_autoconv = incremental_update(autoconv, f_padded, idx, delta, dx, M)

    f_ref = f.copy()
    f_ref[idx] += delta
    autoconv_ref, _, _, _ = make_autoconv(f_ref)

    max_err = np.max(np.abs(new_autoconv - autoconv_ref))
    return max_err


def test_boundary_index(N=500):
    """Test perturbation at boundary indices (idx=0 and idx=N-1)."""
    rng = np.random.default_rng(55)
    f = np.abs(rng.standard_normal(N)) * 0.1
    autoconv, f_padded, dx, M = make_autoconv(f)

    errors = []
    for idx in [0, N-1]:
        delta = 0.01
        new_autoconv = incremental_update(autoconv.copy(), f_padded.copy(), idx, delta, dx, M)

        f_ref = f.copy()
        f_ref[idx] += delta
        autoconv_ref, _, _, _ = make_autoconv(f_ref)

        err = np.max(np.abs(new_autoconv - autoconv_ref))
        errors.append(err)

    return max(errors)


def test_batch_updates(N=500):
    """Test batch_incremental_updates against sequential individual updates."""
    rng = np.random.default_rng(111)
    f = np.abs(rng.standard_normal(N)) * 0.1
    autoconv, f_padded, dx, M = make_autoconv(f)

    # Generate 10 random perturbations
    n_updates = 10
    indices = rng.integers(0, N, size=n_updates)
    deltas = rng.uniform(-0.01, 0.01, size=n_updates)

    # Reference: apply individually
    autoconv_ref = autoconv.copy()
    f_padded_ref = f_padded.copy()
    for idx, delta in zip(indices, deltas):
        autoconv_ref = incremental_update(autoconv_ref, f_padded_ref, int(idx), delta, dx, M)
        f_padded_ref[int(idx)] += delta

    # Batch version
    autoconv_batch = autoconv.copy()
    f_padded_batch = f_padded.copy()
    autoconv_batch, f_padded_batch = batch_incremental_updates(
        autoconv_batch, f_padded_batch, indices, deltas, dx, M
    )

    max_err = np.max(np.abs(autoconv_batch - autoconv_ref))
    return max_err


def test_realistic_array():
    """Test on a realistic-size array (N=2000) similar to TTT-Discover."""
    rng = np.random.default_rng(42)
    N = 2000
    # Sparse-ish array with some structure
    f = np.zeros(N)
    support = rng.integers(0, N, size=300)
    f[support] = np.abs(rng.standard_normal(300)) * 0.5
    f = np.maximum(f, 0.0)

    autoconv, f_padded, dx, M = make_autoconv(f)

    errors = []
    for seed in range(5):
        rng2 = np.random.default_rng(seed + 200)
        idx = int(rng2.integers(0, N))
        delta = rng2.uniform(-f[idx] * 0.5, 0.05)
        new_autoconv = incremental_update(autoconv.copy(), f_padded.copy(), idx, delta, dx, M)
        f_ref = f.copy()
        f_ref[idx] += delta
        autoconv_ref, _, _, _ = make_autoconv(f_ref)
        err = np.max(np.abs(new_autoconv - autoconv_ref))
        errors.append(err)

    return max(errors)


if __name__ == '__main__':
    THRESHOLD = 1e-14
    all_passed = True

    print("=" * 60)
    print("Tests for incremental_autoconv_update.py")
    print("=" * 60)

    # Test 1-5: Five random perturbations (as spec requires)
    print("\n--- 5 random perturbation tests (N=500) ---")
    for seed in range(5):
        err, idx, delta = test_single_perturbation(seed, N=500)
        status = "PASS" if err < THRESHOLD else "FAIL"
        print(f"  Test {seed+1} (idx={idx}, delta={delta:.4f}): max_err={err:.3e} — {status}")
        if err >= THRESHOLD:
            all_passed = False

    # Test 6: Small delta
    print("\n--- Small delta test (delta=1e-12) ---")
    err = test_small_delta()
    status = "PASS" if err < THRESHOLD else "FAIL"
    print(f"  max_err={err:.3e} — {status}")
    if err >= THRESHOLD:
        all_passed = False

    # Test 7: Large delta
    print("\n--- Large delta test (delta=1.0) ---")
    err = test_large_delta()
    status = "PASS" if err < THRESHOLD else "FAIL"
    print(f"  max_err={err:.3e} — {status}")
    if err >= THRESHOLD:
        all_passed = False

    # Test 8: Zero element
    print("\n--- Zero element perturbation ---")
    err = test_zero_element_perturbation()
    status = "PASS" if err < THRESHOLD else "FAIL"
    print(f"  max_err={err:.3e} — {status}")
    if err >= THRESHOLD:
        all_passed = False

    # Test 9: Boundary indices
    print("\n--- Boundary index tests (idx=0 and idx=N-1) ---")
    err = test_boundary_index()
    status = "PASS" if err < THRESHOLD else "FAIL"
    print(f"  max_err={err:.3e} — {status}")
    if err >= THRESHOLD:
        all_passed = False

    # Test 10: Batch updates
    print("\n--- Batch updates test (10 sequential updates) ---")
    err = test_batch_updates()
    status = "PASS" if err < THRESHOLD else "FAIL"
    print(f"  max_err vs individual updates: {err:.3e} — {status}")
    if err >= THRESHOLD:
        all_passed = False

    # Test 11: Realistic array
    print("\n--- Realistic array test (N=2000, 5 perturbations) ---")
    err = test_realistic_array()
    status = "PASS" if err < THRESHOLD else "FAIL"
    print(f"  max_err={err:.3e} — {status}")
    if err >= THRESHOLD:
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)
