"""Tests for find_optimal_shift and analyze_blockers helpers."""

import sys
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem")
sys.path.insert(0, ".")

from helpers.singer import find_singer_set
from helpers.core import is_sidon
from optimal_shift_dev import find_optimal_shift, analyze_blockers


def test_basic_shift():
    """Test with a small known set."""
    # Simple set in Z_7: {0, 1, 3} is a Sidon set
    singer = [0, 1, 3]
    v = 7
    N = 5
    best_shift, truncated = find_optimal_shift(singer, v, N)
    assert all(0 <= x <= N for x in truncated), f"Elements out of range: {truncated}"
    assert is_sidon(truncated), f"Not Sidon: {truncated}"
    # All elements of {0,1,3} are already in [0,5], so best size should be 3
    assert len(truncated) == 3, f"Expected 3, got {len(truncated)}"
    print("PASS: test_basic_shift")


def test_q97_all_fit():
    """q=97: v=9507 < 10001, so ALL shifts should preserve all 98 elements."""
    q = 97
    v = q * q + q + 1  # 9507
    S = find_singer_set(q)
    best_shift, truncated = find_optimal_shift(S, v)
    assert len(truncated) == 98, f"Expected 98, got {len(truncated)}"
    assert is_sidon(truncated), "Not Sidon!"
    assert all(0 <= x <= 10000 for x in truncated)
    print("PASS: test_q97_all_fit")


def test_q101_all_fit():
    """q=101: best shift should preserve all 102 elements."""
    q = 101
    v = q * q + q + 1  # 10303
    S = find_singer_set(q)
    best_shift, truncated = find_optimal_shift(S, v)
    assert len(truncated) == 102, f"Expected 102, got {len(truncated)}"
    assert is_sidon(truncated), "Not Sidon!"
    assert all(0 <= x <= 10000 for x in truncated)
    print("PASS: test_q101_all_fit")


def test_q103_loses_elements():
    """q=103: v=10713, best shift should keep exactly 102 (not all 104)."""
    q = 103
    v = q * q + q + 1  # 10713
    S = find_singer_set(q)
    best_shift, truncated = find_optimal_shift(S, v)
    assert len(truncated) == 102, f"Expected 102, got {len(truncated)}"
    assert is_sidon(truncated), "Not Sidon!"
    assert all(0 <= x <= 10000 for x in truncated)
    print("PASS: test_q103_loses_elements")


def test_q107_loses_more():
    """q=107: v=11557, best shift should keep 99."""
    q = 107
    v = q * q + q + 1  # 11557
    S = find_singer_set(q)
    best_shift, truncated = find_optimal_shift(S, v)
    assert len(truncated) == 99, f"Expected 99, got {len(truncated)}"
    assert is_sidon(truncated), "Not Sidon!"
    print("PASS: test_q107_loses_more")


def test_shift_is_deterministic():
    """Same input should give same output."""
    q = 101
    v = q * q + q + 1
    S = find_singer_set(q)
    s1, t1 = find_optimal_shift(S, v)
    s2, t2 = find_optimal_shift(S, v)
    assert s1 == s2, "Shift not deterministic"
    assert t1 == t2, "Truncated set not deterministic"
    print("PASS: test_shift_is_deterministic")


def test_analyze_blockers_small():
    """Test analyze_blockers on a small Sidon set."""
    S = [0, 1, 3]  # diffs: {1, 2, 3}
    N = 6
    blockers = analyze_blockers(S, N)
    # Non-members: 2, 4, 5, 6
    assert set(blockers.keys()) == {2, 4, 5, 6}, f"Wrong non-members: {set(blockers.keys())}"
    # Element 2: |2-0|=2 (in diffs), |2-1|=1 (in diffs), |2-3|=1 (in diffs) → 3 blockers
    assert blockers[2] == 3, f"Expected 3 blockers for 2, got {blockers[2]}"
    # Element 4: |4-0|=4 (not in diffs), |4-1|=3 (in diffs), |4-3|=1 (in diffs) → 2 blockers
    assert blockers[4] == 2, f"Expected 2 blockers for 4, got {blockers[4]}"
    # Element 5: |5-0|=5 (not), |5-1|=4 (not), |5-3|=2 (in diffs) → 1 blocker
    assert blockers[5] == 1, f"Expected 1 blocker for 5, got {blockers[5]}"
    # Element 6: |6-0|=6 (not), |6-1|=5 (not), |6-3|=3 (in diffs) → 1 blocker
    assert blockers[6] == 1, f"Expected 1 blocker for 6, got {blockers[6]}"
    print("PASS: test_analyze_blockers_small")


def test_analyze_blockers_q101():
    """Test that q=101 truncated set has min blockers >= 40."""
    q = 101
    v = q * q + q + 1
    S = find_singer_set(q)
    _, truncated = find_optimal_shift(S, v)
    blockers = analyze_blockers(truncated)
    min_b = min(blockers.values())
    assert min_b >= 40, f"Expected min blockers >= 40, got {min_b}"
    print(f"PASS: test_analyze_blockers_q101 (min={min_b})")


def test_truncated_sorted():
    """Verify truncated set is returned sorted."""
    q = 103
    v = q * q + q + 1
    S = find_singer_set(q)
    _, truncated = find_optimal_shift(S, v)
    assert truncated == sorted(truncated), "Truncated set not sorted"
    print("PASS: test_truncated_sorted")


if __name__ == "__main__":
    test_basic_shift()
    test_q97_all_fit()
    test_q101_all_fit()
    test_q103_loses_elements()
    test_q107_loses_more()
    test_shift_is_deterministic()
    test_analyze_blockers_small()
    test_analyze_blockers_q101()
    test_truncated_sorted()
    print("\n=== ALL TESTS PASSED ===")
