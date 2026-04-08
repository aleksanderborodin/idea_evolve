"""Utility functions for extending and perturbing Sidon sets.

A Sidon set (B2 sequence) has all pairwise differences distinct.
These helpers use Python sets for O(k) per-candidate difference checks,
making greedy extension O(N*k) overall.

Usage:
    from helpers.extend import greedy_extend, count_addable, random_perturbation, blocking_power
    from helpers.rokicki_data import BEST_105
    extended = greedy_extend(BEST_105[:100])
    print(len(extended))
"""

import random


def greedy_extend(initial_set, N=10000):
    """Greedily add elements to a Sidon set.

    Iterates through {0..N} in order and adds each element if it preserves the
    Sidon property. Uses a set of used differences for O(k) per-candidate check.

    Args:
        initial_set: Iterable of integers forming a valid Sidon set (sorted or unsorted).
        N: Upper bound of the search range (inclusive). Default: 10000.

    Returns:
        Sorted list of integers forming the extended Sidon set.

    Example:
        >>> from helpers.rokicki_data import BEST_105
        >>> result = greedy_extend(BEST_105[:100])
        >>> len(result) >= 100
        True
    """
    S = sorted(set(initial_set))
    s_set = set(S)
    diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            diffs.add(S[j] - S[i])

    for c in range(N + 1):
        if c in s_set:
            continue
        new_diffs = set()
        ok = True
        for x in S:
            d = abs(c - x)
            if d in diffs or d in new_diffs:
                ok = False
                break
            new_diffs.add(d)
        if ok:
            S.append(c)
            s_set.add(c)
            diffs.update(new_diffs)

    return sorted(S)


def count_addable(S, N=10000):
    """Count how many elements in {0..N} can be individually added to S.

    An element is "addable" if adding it to S preserves the Sidon property.
    A greedy-maximal set will have count_addable == 0.

    Args:
        S: Iterable of integers forming a valid Sidon set.
        N: Upper bound of the search range (inclusive). Default: 10000.

    Returns:
        Integer count of addable elements.

    Example:
        >>> from helpers.rokicki_data import BEST_105
        >>> count_addable(BEST_105)  # greedy-maximal → 0
        0
    """
    S = sorted(set(S))
    s_set = set(S)
    diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            diffs.add(S[j] - S[i])

    count = 0
    for c in range(N + 1):
        if c in s_set:
            continue
        ok = True
        new_diffs = set()
        for x in S:
            d = abs(c - x)
            if d in diffs or d in new_diffs:
                ok = False
                break
            new_diffs.add(d)
        if ok:
            count += 1
    return count


def random_perturbation(S, k, N=10000, seed=None):
    """Remove k random elements from S, then greedily re-extend.

    Args:
        S: Iterable of integers forming a valid Sidon set.
        k: Number of elements to remove (perturbation size).
        N: Upper bound of the search range (inclusive). Default: 10000.
        seed: Optional random seed for reproducibility.

    Returns:
        Sorted list of integers forming the perturbed+extended Sidon set.
        May be larger or smaller than the original S.

    Example:
        >>> from helpers.rokicki_data import BEST_105
        >>> from helpers.core import is_sidon
        >>> result = random_perturbation(BEST_105, 3, seed=42)
        >>> is_sidon(result)
        True
    """
    S_list = sorted(set(S))
    rng = random.Random(seed)
    k = min(k, len(S_list))
    to_remove = set(rng.sample(S_list, k))
    remaining = [x for x in S_list if x not in to_remove]
    return greedy_extend(remaining, N)


def blocking_power(S, N=10000):
    """For each element in S, count how many potential elements it blocks.

    An element x in S "blocks" a candidate c if the difference |c - x| already
    appears in S's difference set (making c un-addable due to x).

    Note: A candidate may be blocked by multiple elements; each blocking
    relationship is counted once per (element, candidate) pair.

    Args:
        S: Iterable of integers forming a valid Sidon set.
        N: Upper bound of the search range (inclusive). Default: 10000.

    Returns:
        Dict mapping each element of S to its blocking count (int).

    Example:
        >>> from helpers.rokicki_data import BEST_105
        >>> bp = blocking_power(BEST_105)
        >>> max(bp.values()) > 0
        True
    """
    S_list = sorted(set(S))
    s_set = set(S_list)
    diffs = set()
    for i in range(len(S_list)):
        for j in range(i + 1, len(S_list)):
            diffs.add(S_list[j] - S_list[i])

    blocker_count = {e: 0 for e in S_list}

    for c in range(N + 1):
        if c in s_set:
            continue
        for x in S_list:
            d = abs(c - x)
            if d in diffs:
                blocker_count[x] += 1

    return blocker_count


if __name__ == "__main__":
    import sys
    import os
    # Allow running from any location
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    try:
        from helpers.rokicki_data import BEST_105
        from helpers.core import is_sidon
    except ImportError:
        # Fallback for direct execution
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        from helpers.rokicki_data import BEST_105
        from helpers.core import is_sidon

    print("=== Testing extend.py helpers ===")
    print(f"BEST_105 length: {len(BEST_105)}")
    assert is_sidon(BEST_105), "BEST_105 must be a valid Sidon set"

    # Test greedy_extend
    print("\n1. Testing greedy_extend...")
    result = greedy_extend(BEST_105[:100])
    assert len(result) >= 100, f"Expected >= 100 elements, got {len(result)}"
    assert is_sidon(result), "greedy_extend result must be valid Sidon set"
    print(f"   greedy_extend(BEST_105[:100]) -> {len(result)} elements (>= 100) ✓")

    # Test count_addable
    print("\n2. Testing count_addable...")
    addable = count_addable(BEST_105)
    assert addable == 0, f"BEST_105 should be greedy-maximal (0 addable), got {addable}"
    print(f"   count_addable(BEST_105) -> {addable} (greedy-maximal confirmed) ✓")

    # Test random_perturbation
    print("\n3. Testing random_perturbation...")
    result = random_perturbation(BEST_105, 3, seed=42)
    assert is_sidon(result), "random_perturbation result must be valid Sidon set"
    print(f"   random_perturbation(BEST_105, k=3) -> {len(result)} elements, valid Sidon ✓")

    # Test blocking_power
    print("\n4. Testing blocking_power...")
    bp = blocking_power(BEST_105)
    assert len(bp) == len(BEST_105), "blocking_power must return entry for each element"
    assert all(v >= 0 for v in bp.values()), "All blocking counts must be non-negative"
    max_blocker = max(bp, key=bp.get)
    print(f"   blocking_power(BEST_105): max blocker = {max_blocker} ({bp[max_blocker]} blocks) ✓")

    print("\n=== All tests passed ===")
