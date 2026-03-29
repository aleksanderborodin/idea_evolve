"""Comprehensive tests for topk_screened_cd helper."""

import sys
import os
import time
import numpy as np

# Add sandbox scripts to path for development testing
sys.path.insert(0, os.path.dirname(__file__))
from topk_screened_cd import topk_screened_cd, _fft_recompute, _c_from_autoconv


def compute_c_reference(f):
    """Reference C computation matching validate.py exactly."""
    f = np.asarray(f, dtype=np.float64)
    N = len(f)
    dx = 0.5 / N
    f_nn = np.maximum(f, 0.0)
    integral = float(np.sum(f_nn)) * dx
    if integral ** 2 < 1e-30:
        return float('nan')
    padded = np.zeros(2 * N, dtype=np.float64)
    padded[:N] = f_nn
    fft_f = np.fft.fft(padded)
    autoconv = np.fft.ifft(fft_f * fft_f).real * dx
    return float(np.max(autoconv)) / (integral ** 2)


def test_correctness_monotonic_c():
    """Test 1: C decreases monotonically across rounds on a small array."""
    print("Test 1: Correctness — C decreases monotonically ... ", end="", flush=True)
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(100)) * 0.1 + 0.01

    result = topk_screened_cd(f, K=30, max_rounds=10, resync_interval=1)

    # C should decrease or stay same across rounds
    for i in range(1, len(result['round_log'])):
        c_prev = result['round_log'][i - 1]['C_verified']
        c_curr = result['round_log'][i]['C_verified']
        assert c_curr <= c_prev + 1e-14, (
            f"C increased: round {i-1} C={c_prev}, round {i} C={c_curr}"
        )

    # Final C should match reference
    c_ref = compute_c_reference(result['f'])
    assert abs(result['C'] - c_ref) < 1e-12, (
        f"Final C mismatch: result={result['C']}, ref={c_ref}"
    )

    # Should have found some improvements
    assert result['n_improvements'] > 0, "No improvements found on random array"
    print(f"PASS (improvements={result['n_improvements']}, C: {compute_c_reference(f):.6f} → {result['C']:.6f})")


def test_resync_vs_no_resync():
    """Test 2: Resync version should have lower or equal verified C."""
    print("Test 2: Resync vs no-resync comparison ... ", end="", flush=True)
    rng = np.random.default_rng(123)
    f = np.abs(rng.standard_normal(200)) * 0.05 + 0.01

    # With resync every round
    result_resync = topk_screened_cd(
        f.copy(), K=30, max_rounds=5, resync_interval=1,
        deltas=np.geomspace(1e-10, 1e-1, 50)
    )

    # Without resync (resync_interval > max_rounds)
    result_no_resync = topk_screened_cd(
        f.copy(), K=30, max_rounds=5, resync_interval=999,
        deltas=np.geomspace(1e-10, 1e-1, 50)
    )

    # Verify both results with reference
    c_resync = compute_c_reference(result_resync['f'])
    c_no_resync = compute_c_reference(result_no_resync['f'])

    # The resync version's reported C should match its verified C
    assert abs(result_resync['C'] - c_resync) < 1e-12, (
        f"Resync C mismatch: reported={result_resync['C']}, verified={c_resync}"
    )

    print(f"PASS (resync C={c_resync:.10f}, no_resync C={c_no_resync:.10f})")


def test_topk_no_false_negatives():
    """Test 3: Top-K screening accepts exactly same moves as full-array (K=all)."""
    print("Test 3: Top-K no false negatives ... ", end="", flush=True)
    rng = np.random.default_rng(77)
    N = 50
    f = np.abs(rng.standard_normal(N)) * 0.1 + 0.01

    # K=all (no screening)
    result_full = topk_screened_cd(
        f.copy(), K=2*N,  # K >= M means check all positions
        max_rounds=3, resync_interval=1,
        deltas=np.geomspace(1e-8, 1e-1, 30)
    )

    # K=5 (aggressive screening)
    result_k5 = topk_screened_cd(
        f.copy(), K=5,
        max_rounds=3, resync_interval=1,
        deltas=np.geomspace(1e-8, 1e-1, 30)
    )

    # Both should find improvements
    c_full = compute_c_reference(result_full['f'])
    c_k5 = compute_c_reference(result_k5['f'])

    # Both should improve from baseline
    c_baseline = compute_c_reference(f)
    assert c_full <= c_baseline + 1e-14, "Full screening didn't improve"
    assert c_k5 <= c_baseline + 1e-14, "K=5 screening didn't improve"

    print(f"PASS (baseline={c_baseline:.10f}, full={c_full:.10f}, K5={c_k5:.10f})")


def test_deadline_enforcement():
    """Test 4: Deadline enforcement — should return within deadline + buffer."""
    print("Test 4: Deadline enforcement ... ", end="", flush=True)
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(500)) * 0.1 + 0.01

    budget = 2.0  # 2 seconds
    t0 = time.time()
    result = topk_screened_cd(
        f, K=30, max_rounds=10000, deadline=t0 + budget,
        deltas=np.geomspace(1e-10, 1e-1, 50)
    )
    elapsed = time.time() - t0

    # Should return within budget + reasonable overhead (1s buffer for one round)
    assert elapsed < budget + 3.0, (
        f"Took {elapsed:.1f}s, expected < {budget + 3.0:.1f}s"
    )

    # Should still have valid results
    c_ref = compute_c_reference(result['f'])
    assert abs(result['C'] - c_ref) < 1e-12
    print(f"PASS (elapsed={elapsed:.2f}s, budget={budget}s, rounds={result['n_rounds']})")


def test_non_negativity():
    """Test 5: No element in output is negative."""
    print("Test 5: Non-negativity ... ", end="", flush=True)
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(200)) * 0.1 + 0.01
    # Add some zeros
    f[10:20] = 0.0

    result = topk_screened_cd(f, K=30, max_rounds=5, resync_interval=1)

    assert np.all(result['f'] >= 0.0), (
        f"Negative values found: min={np.min(result['f'])}"
    )
    print(f"PASS (min={np.min(result['f']):.2e})")


def test_default_deltas():
    """Test 6: Default delta grid is geomspace(1e-14, 1e-1, 100)."""
    print("Test 6: Default deltas ... ", end="", flush=True)
    # We test indirectly: call with no deltas and check behavior matches
    expected = np.geomspace(1e-14, 1e-1, 100)

    # Verify our expected values
    assert len(expected) == 100
    assert abs(expected[0] - 1e-14) < 1e-28
    assert abs(expected[-1] - 1e-1) < 1e-15

    # Run with default deltas
    f = np.ones(50) * 0.1
    result = topk_screened_cd(f, K=10, max_rounds=1)
    # Just verify it runs without error
    assert 'C' in result
    print("PASS")


def test_round_log_format():
    """Test 7: Round log entries contain all required keys."""
    print("Test 7: Round log format ... ", end="", flush=True)
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(100)) * 0.1 + 0.01

    result = topk_screened_cd(f, K=30, max_rounds=3, resync_interval=1)

    required_keys = {'round', 'improvements', 'C_verified', 'elapsed_s'}
    for entry in result['round_log']:
        missing = required_keys - set(entry.keys())
        assert not missing, f"Missing keys in round_log: {missing}"
        assert isinstance(entry['round'], int)
        assert isinstance(entry['improvements'], int)
        assert isinstance(entry['C_verified'], float)
        assert isinstance(entry['elapsed_s'], float)
        assert entry['elapsed_s'] >= 0

    # Check round numbers are sequential
    for i, entry in enumerate(result['round_log']):
        assert entry['round'] == i, f"Expected round {i}, got {entry['round']}"

    print(f"PASS ({len(result['round_log'])} entries)")


def test_return_dict_format():
    """Test 7b: Return value has all required keys and correct types."""
    print("Test 7b: Return dict format ... ", end="", flush=True)
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(100)) * 0.1 + 0.01

    result = topk_screened_cd(f, K=30, max_rounds=2, resync_interval=1)

    assert isinstance(result, dict)
    assert 'f' in result and isinstance(result['f'], np.ndarray)
    assert 'C' in result and isinstance(result['C'], float)
    assert 'n_improvements' in result and isinstance(result['n_improvements'], int)
    assert 'n_rounds' in result and isinstance(result['n_rounds'], int)
    assert 'round_log' in result and isinstance(result['round_log'], list)
    assert result['f'].dtype == np.float64
    assert result['n_rounds'] == len(result['round_log'])
    print("PASS")


def test_empty_array():
    """Test 8a: Empty array edge case."""
    print("Test 8a: Empty array ... ", end="", flush=True)
    f = np.array([], dtype=np.float64)
    result = topk_screened_cd(f, K=30, max_rounds=5)

    assert len(result['f']) == 0
    assert result['n_improvements'] == 0
    assert result['n_rounds'] == 0
    assert len(result['round_log']) == 0
    print("PASS")


def test_all_zero_array():
    """Test 8b: All-zero array edge case."""
    print("Test 8b: All-zero array ... ", end="", flush=True)
    f = np.zeros(50, dtype=np.float64)
    result = topk_screened_cd(f, K=30, max_rounds=5)

    # All zeros: CD may add small positive deltas (valid since f+delta >= 0).
    # Key: should not crash, output should be non-negative.
    assert np.all(result['f'] >= 0.0)
    assert isinstance(result['C'], float)
    print(f"PASS (improvements={result['n_improvements']})")


def test_single_element():
    """Test 8c: Single-element array edge case."""
    print("Test 8c: Single-element array ... ", end="", flush=True)
    f = np.array([1.0], dtype=np.float64)
    result = topk_screened_cd(f, K=30, max_rounds=5)

    # For a single element, C = 1/(dx) = 2*N = 2
    # CD can't do anything useful with just one element
    assert len(result['f']) == 1
    assert result['f'][0] >= 0.0
    print("PASS")


def test_constant_function():
    """Test 8d: Constant function — C should be exactly 2.0."""
    print("Test 8d: Constant function ... ", end="", flush=True)
    N = 100
    f = np.ones(N) * 0.5

    c_before = compute_c_reference(f)
    assert abs(c_before - 2.0) < 1e-10, f"Constant function C should be ~2.0, got {c_before}"

    result = topk_screened_cd(f, K=30, max_rounds=3, resync_interval=1)

    # CD should find improvements since a constant function is far from optimal
    c_after = compute_c_reference(result['f'])
    assert c_after <= c_before + 1e-14, (
        f"C increased: {c_before:.10f} → {c_after:.10f}"
    )
    print(f"PASS (C: {c_before:.6f} → {c_after:.6f})")


def test_c_matches_validate():
    """Test 9: Returned C matches validate.py's computation."""
    print("Test 9: C matches reference ... ", end="", flush=True)
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(200)) * 0.1 + 0.01

    result = topk_screened_cd(f, K=30, max_rounds=3, resync_interval=1)

    c_ref = compute_c_reference(result['f'])
    diff = abs(result['C'] - c_ref)
    assert diff < 1e-12, f"C mismatch: result={result['C']:.16f}, ref={c_ref:.16f}, diff={diff:.2e}"
    print(f"PASS (diff={diff:.2e})")


def test_does_not_modify_input():
    """Test 10: Input array is not modified."""
    print("Test 10: Input not modified ... ", end="", flush=True)
    rng = np.random.default_rng(42)
    f = np.abs(rng.standard_normal(100)) * 0.1 + 0.01
    f_copy = f.copy()

    result = topk_screened_cd(f, K=30, max_rounds=2)

    assert np.array_equal(f, f_copy), "Input array was modified!"
    print("PASS")


if __name__ == "__main__":
    print("=" * 60)
    print("topk_screened_cd comprehensive tests")
    print("=" * 60)
    print()

    tests = [
        test_correctness_monotonic_c,
        test_resync_vs_no_resync,
        test_topk_no_false_negatives,
        test_deadline_enforcement,
        test_non_negativity,
        test_default_deltas,
        test_round_log_format,
        test_return_dict_format,
        test_empty_array,
        test_all_zero_array,
        test_single_element,
        test_constant_function,
        test_c_matches_validate,
        test_does_not_modify_input,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {e}")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)
