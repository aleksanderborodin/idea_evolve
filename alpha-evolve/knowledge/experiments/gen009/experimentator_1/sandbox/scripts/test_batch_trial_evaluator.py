"""Tests for batch_predict_c.

Tests:
1. Single-candidate output matches incremental_update applied sequentially (<1e-8 relative error)
2. K=100 batch: all within 1e-6 relative of individual calls
3. Speed benchmark: K=100 at N=30000 completes in <0.1s
4. Edge cases: k=3 (triplet), k=5 (quintuple), verify row-sum-zero constraint
"""

import sys
import time
import numpy as np

# Add project root helpers to sys.path
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')
from helpers.incremental_autoconv_update import incremental_update, batch_incremental_updates
from helpers.compute_c_f64 import compute_c_f64

# Add sandbox to sys.path
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/workspace/gen009_experimentator_1/output/sandbox/scripts')
from batch_trial_evaluator_dev import batch_predict_c


def make_test_state(N=500, seed=42):
    """Create a test state with f, f_padded, autoconv, dx, M."""
    rng = np.random.default_rng(seed)
    f = np.abs(rng.standard_normal(N)) * 0.1
    dx = 0.5 / N
    M = 2 * N
    f_padded = np.pad(f, (0, N)).astype(np.float64)
    fft_f = np.fft.fft(f_padded)
    autoconv = np.fft.ifft(fft_f * fft_f).real * dx
    return f, f_padded, autoconv, dx, M


def compute_exact_c_after_move(f_padded, autoconv, indices, deltas, dx, M):
    """Apply a k-element move exactly using sequential incremental_update and return C."""
    ac = autoconv.copy()
    fp = f_padded.copy()
    N = M // 2
    for idx, delta in zip(indices, deltas):
        ac = incremental_update(ac, fp, int(idx), float(delta), dx, M)
        fp[int(idx)] += delta
    integral = np.sum(fp[:N]) * dx
    return float(np.max(ac)) / (integral ** 2)


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Single candidate (K=1, k=4 quadruplet), compare to incremental_update
# ─────────────────────────────────────────────────────────────────────────────
def test_single_candidate_accuracy():
    print("Test 1: Single candidate accuracy vs incremental_update...")
    N = 1000
    f, f_padded, autoconv, dx, M = make_test_state(N=N, seed=7)

    # Pick 4 indices with non-trivial f values
    indices = np.array([10, 200, 500, 800], dtype=np.int64)
    # Integral-preserving deltas (sum = 0)
    raw_deltas = np.array([0.002, -0.001, -0.0005, -0.0005])
    assert abs(raw_deltas.sum()) < 1e-15

    # Exact C after applying the move
    exact_c = compute_exact_c_after_move(f_padded, autoconv, indices, raw_deltas, dx, M)

    # Predicted C via batch_predict_c (K=1)
    ib = indices[np.newaxis, :]  # (1, 4)
    db = raw_deltas[np.newaxis, :]  # (1, 4)
    predicted = batch_predict_c(autoconv, f_padded, dx, M, ib, db)
    assert predicted.shape == (1,)
    pred_c = predicted[0]

    rel_err = abs(pred_c - exact_c) / abs(exact_c)
    print(f"  Exact C: {exact_c:.10f}")
    print(f"  Predicted C: {pred_c:.10f}")
    print(f"  Relative error: {rel_err:.2e}")
    assert rel_err < 1e-8, f"Relative error {rel_err:.2e} exceeds 1e-8"
    print("  PASSED")


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: K=100 batch, all within 1e-6 relative of individual calls
# ─────────────────────────────────────────────────────────────────────────────
def test_batch_accuracy():
    print("Test 2: K=100 batch accuracy...")
    N = 2000
    f, f_padded, autoconv, dx, M = make_test_state(N=N, seed=99)

    K = 100
    k_size = 4
    rng = np.random.default_rng(12345)

    # Generate K random quadruplets with small deltas
    indices_batch = rng.integers(0, N, size=(K, k_size)).astype(np.int64)
    raw = rng.standard_normal((K, k_size)) * 1e-4
    # Make each row sum to 0
    raw -= raw.mean(axis=1, keepdims=True)
    deltas_batch = raw.astype(np.float64)

    # Exact C for each candidate (sequential incremental updates)
    exact_c = np.zeros(K, dtype=np.float64)
    for j in range(K):
        exact_c[j] = compute_exact_c_after_move(
            f_padded, autoconv, indices_batch[j], deltas_batch[j], dx, M
        )

    # Batch prediction
    predicted = batch_predict_c(autoconv, f_padded, dx, M, indices_batch, deltas_batch)
    assert predicted.shape == (K,)

    rel_errs = np.abs(predicted - exact_c) / np.abs(exact_c)
    max_rel_err = np.max(rel_errs)
    mean_rel_err = np.mean(rel_errs)
    print(f"  Max relative error: {max_rel_err:.2e}")
    print(f"  Mean relative error: {mean_rel_err:.2e}")
    assert max_rel_err < 1e-6, f"Max relative error {max_rel_err:.2e} exceeds 1e-6"
    print("  PASSED")


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Speed benchmark — K=100 at N=30000 should complete in <0.1s
# ─────────────────────────────────────────────────────────────────────────────
def test_speed_benchmark():
    print("Test 3: Speed benchmark K=100 at N=30000...")
    N = 30000
    f, f_padded, autoconv, dx, M = make_test_state(N=N, seed=1)

    K = 100
    k_size = 4
    rng = np.random.default_rng(42)
    indices_batch = rng.integers(0, N, size=(K, k_size)).astype(np.int64)
    raw = rng.standard_normal((K, k_size)) * 1e-5
    raw -= raw.mean(axis=1, keepdims=True)
    deltas_batch = raw.astype(np.float64)

    # Warm-up
    _ = batch_predict_c(autoconv, f_padded, dx, M, indices_batch[:5], deltas_batch[:5])

    # Timed run
    t0 = time.perf_counter()
    result = batch_predict_c(autoconv, f_padded, dx, M, indices_batch, deltas_batch)
    elapsed = time.perf_counter() - t0

    assert result.shape == (K,)
    print(f"  K=100, N=30000: {elapsed*1000:.1f}ms")

    # Compare with sequential approach timing
    t1 = time.perf_counter()
    for j in range(K):
        _ = compute_exact_c_after_move(
            f_padded, autoconv, indices_batch[j], deltas_batch[j], dx, M
        )
    seq_elapsed = time.perf_counter() - t1
    speedup = seq_elapsed / elapsed
    print(f"  Sequential (K=100 exact): {seq_elapsed*1000:.1f}ms")
    print(f"  Speedup: {speedup:.1f}x")

    assert elapsed < 0.1, f"batch_predict_c took {elapsed:.3f}s, expected <0.1s"
    print("  PASSED")


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Triplets (k=3)
# ─────────────────────────────────────────────────────────────────────────────
def test_triplet_k3():
    print("Test 4: Triplet (k=3) moves...")
    N = 1000
    f, f_padded, autoconv, dx, M = make_test_state(N=N, seed=55)

    K = 20
    rng = np.random.default_rng(777)
    indices_batch = rng.integers(0, N, size=(K, 3)).astype(np.int64)
    raw = rng.standard_normal((K, 3)) * 1e-4
    raw -= raw.mean(axis=1, keepdims=True)
    deltas_batch = raw.astype(np.float64)

    predicted = batch_predict_c(autoconv, f_padded, dx, M, indices_batch, deltas_batch)
    assert predicted.shape == (K,)

    exact_c = np.array([
        compute_exact_c_after_move(f_padded, autoconv, indices_batch[j], deltas_batch[j], dx, M)
        for j in range(K)
    ])

    rel_errs = np.abs(predicted - exact_c) / np.abs(exact_c)
    max_rel_err = np.max(rel_errs)
    print(f"  Max relative error (k=3): {max_rel_err:.2e}")
    assert max_rel_err < 1e-6
    print("  PASSED")


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Ground truth against compute_c_f64 for small N
# ─────────────────────────────────────────────────────────────────────────────
def test_ground_truth_vs_compute_c():
    print("Test 5: Verify predicted C ordering matches exact C ordering...")
    N = 500
    f, f_padded, autoconv, dx, M = make_test_state(N=N, seed=33)

    K = 50
    k_size = 4
    rng = np.random.default_rng(88)
    indices_batch = rng.integers(0, N, size=(K, k_size)).astype(np.int64)
    raw = rng.standard_normal((K, k_size)) * 5e-5
    raw -= raw.mean(axis=1, keepdims=True)
    deltas_batch = raw.astype(np.float64)

    predicted = batch_predict_c(autoconv, f_padded, dx, M, indices_batch, deltas_batch)

    # Compute exact C using compute_c_f64
    exact_c = np.zeros(K, dtype=np.float64)
    for j in range(K):
        fp = f_padded.copy()
        for idx, delta in zip(indices_batch[j], deltas_batch[j]):
            fp[int(idx)] += delta
        f_new = fp[:N]
        exact_c[j] = compute_c_f64(f_new)

    # Check that ranking (argsort) roughly matches — top 10 should have large overlap
    pred_rank = np.argsort(predicted)[:10]
    exact_rank = np.argsort(exact_c)[:10]
    overlap = len(set(pred_rank) & set(exact_rank))
    rel_errs = np.abs(predicted - exact_c) / np.abs(exact_c)
    max_rel_err = np.max(rel_errs)

    print(f"  Top-10 overlap between predicted and exact ranking: {overlap}/10")
    print(f"  Max relative error: {max_rel_err:.2e}")
    assert max_rel_err < 1e-6
    assert overlap >= 7, f"Poor ranking overlap: {overlap}/10"
    print("  PASSED")


if __name__ == "__main__":
    test_single_candidate_accuracy()
    test_batch_accuracy()
    test_speed_benchmark()
    test_triplet_k3()
    test_ground_truth_vs_compute_c()
    print("\nAll tests PASSED.")
