"""Development and testing of greedy_sidon and build_diff_counts."""
import sys
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon")
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/workspace/gen002_experimentator_1/output/sandbox/scripts")
from helpers.core import is_sidon
from dev_singer import find_singer_set


def greedy_sidon(candidates, N=10000):
    """Build the largest Sidon set by greedily selecting from candidates in order.

    For each candidate (in the given order), add it to the set if it doesn't
    create a repeated difference. Maintains used_diffs incrementally for speed.

    Args:
        candidates: ordered iterable of candidate integers
        N: maximum allowed value (elements > N are skipped)

    Returns:
        sorted list forming a valid Sidon set

    Examples:
        >>> len(greedy_sidon(range(10001)))
        66
        >>> S97 = find_singer_set(97)
        >>> len(greedy_sidon(S97))
        98
    """
    S = []
    used_diffs = set()
    for c in candidates:
        if c < 0 or c > N:
            continue
        new_diffs = []
        ok = True
        for x in S:
            d = abs(c - x)
            if d in used_diffs or d in set(new_diffs):
                ok = False
                break
            new_diffs.append(d)
        if ok:
            S.append(c)
            used_diffs.update(new_diffs)
    return sorted(S)


def build_diff_counts(S):
    """Build a dictionary mapping each positive difference to its count.

    For a valid Sidon set, every count should be exactly 1.
    Useful for local search to track which differences are in use.

    Args:
        S: sorted list of integers (a Sidon set)

    Returns:
        dict mapping each positive difference d to the number of pairs
        (i, j) in S with S[j] - S[i] = d

    Examples:
        >>> S = [0, 1, 3, 7]
        >>> d = build_diff_counts(S)
        >>> all(v == 1 for v in d.values())
        True
        >>> len(d)
        6
    """
    S = sorted(S)
    counts = {}
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            d = S[j] - S[i]
            counts[d] = counts.get(d, 0) + 1
    return counts


# Tests
if __name__ == "__main__":
    print("Testing greedy_sidon...")

    # Test 1: greedy from 0..10000 should give exactly 66 elements
    g = greedy_sidon(range(10001))
    print(f"  greedy_sidon(range(10001)): {len(g)} elements")
    assert len(g) == 66, f"Expected 66, got {len(g)}"
    assert is_sidon(g), "Greedy result is not Sidon!"
    assert all(0 <= x <= 10000 for x in g), "Elements out of range"
    print("  PASS: baseline = 66")

    # Test 2: greedy on Singer q=97 set should return all 98 (already Sidon)
    S97 = find_singer_set(97)
    g97 = greedy_sidon(S97)
    print(f"  greedy_sidon(singer_97): {len(g97)} elements")
    assert len(g97) == 98, f"Expected 98, got {len(g97)}"
    assert is_sidon(g97), "Greedy on Singer is not Sidon!"
    print("  PASS: Singer set preserved")

    # Test 3: empty input
    g_empty = greedy_sidon([])
    assert g_empty == [], f"Expected empty, got {g_empty}"
    print("  PASS: empty input")

    # Test 4: single element
    g_one = greedy_sidon([5])
    assert g_one == [5], f"Expected [5], got {g_one}"
    print("  PASS: single element")

    # Test 5: elements beyond N are skipped
    g_bounded = greedy_sidon([0, 1, 3, 7, 20000])
    assert 20000 not in g_bounded, "Should skip elements > N"
    print("  PASS: N boundary")

    print("\nTesting build_diff_counts...")

    # Test 1: small Sidon set
    d = build_diff_counts([0, 1, 3, 7])
    print(f"  build_diff_counts([0,1,3,7]): {len(d)} diffs, all_ones={all(v==1 for v in d.values())}")
    assert len(d) == 6, f"Expected 6 diffs (C(4,2)), got {len(d)}"
    assert all(v == 1 for v in d.values()), "Not all counts are 1!"
    assert d[1] == 1 and d[3] == 1 and d[7] == 1  # 1-0, 3-0, 7-0
    assert d[2] == 1 and d[6] == 1 and d[4] == 1  # 3-1, 7-1, 7-3
    print("  PASS: small set")

    # Test 2: Singer q=97 — all diffs should be 1, count = C(98,2) = 4753
    d97 = build_diff_counts(S97)
    n_diffs = len(d97)
    expected_diffs = 98 * 97 // 2  # C(98,2) = 4753
    print(f"  build_diff_counts(singer_97): {n_diffs} diffs, expected {expected_diffs}")
    assert n_diffs == expected_diffs, f"Expected {expected_diffs} diffs, got {n_diffs}"
    assert all(v == 1 for v in d97.values()), "Singer q=97 has repeated diffs!"
    print("  PASS: Singer q=97")

    # Test 3: empty set
    d_empty = build_diff_counts([])
    assert d_empty == {}, f"Expected empty dict, got {d_empty}"
    print("  PASS: empty set")

    # Test 4: non-Sidon set should have counts > 1
    d_bad = build_diff_counts([0, 1, 2, 3])  # diff 1: (1-0, 2-1, 3-2) = 3 times
    assert d_bad[1] == 3, f"Expected count 3 for diff 1, got {d_bad.get(1)}"
    assert d_bad[2] == 2, f"Expected count 2 for diff 2, got {d_bad.get(2)}"
    print("  PASS: non-Sidon detection")

    print("\nAll search helper tests passed!")
