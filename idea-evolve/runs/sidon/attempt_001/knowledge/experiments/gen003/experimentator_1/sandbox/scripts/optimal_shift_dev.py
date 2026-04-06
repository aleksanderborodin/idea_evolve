"""Development version of find_optimal_shift and analyze_blockers."""

import sys
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem")

from helpers.singer import find_singer_set
from helpers.core import is_sidon


def find_optimal_shift(singer_set, v, N=10000):
    """
    Given a Singer set in Z_v, find the cyclic shift d that maximizes
    the number of elements in {0, ..., N}.

    Args:
        singer_set: list of integers in Z_v (the raw Singer set)
        v: the modulus (q^2 + q + 1)
        N: upper bound of target range (default 10000)

    Returns:
        (best_shift, truncated_set) where truncated_set is the sorted list
        of elements in {0, ..., N} after applying the best shift.
    """
    best_shift = 0
    best_count = 0
    best_set = []

    s_set = set(singer_set)

    for d in range(v):
        shifted = [(s + d) % v for s in singer_set]
        truncated = sorted(x for x in shifted if x <= N)
        if len(truncated) > best_count:
            best_count = len(truncated)
            best_shift = d
            best_set = truncated

    return best_shift, best_set


def analyze_blockers(sidon_set, N=10000):
    """For each non-member in {0,...,N}, count how many current members block it.

    An element c is "blocked" by a member x if the difference |c - x| already
    appears as a difference between two existing members. The blocker count
    is the number of members x that create such a conflict.

    Args:
        sidon_set: list of integers forming a valid Sidon set
        N: upper bound of range (default 10000)

    Returns:
        dict mapping each non-member in {0,...,N} to its blocker count.
        Higher count = harder to add this element.
    """
    S = sorted(sidon_set)
    s_set = set(S)

    # Build the set of existing differences
    used_diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            used_diffs.add(S[j] - S[i])

    blockers = {}
    for c in range(N + 1):
        if c in s_set:
            continue
        count = 0
        for x in S:
            d = abs(c - x)
            if d in used_diffs:
                count += 1
        blockers[c] = count

    return blockers


if __name__ == "__main__":
    # Test on q=101
    print("=== Testing q=101 ===")
    q = 101
    v = q * q + q + 1
    S = find_singer_set(q)
    print(f"Singer set size: {len(S)}, v={v}")

    best_shift, truncated = find_optimal_shift(S, v)
    print(f"Best shift: {best_shift}, truncated size: {len(truncated)}")
    print(f"Is Sidon: {is_sidon(truncated)}")
    print(f"Min element: {min(truncated)}, Max element: {max(truncated)}")

    # Count how many shifts preserve all elements
    all_fit_count = 0
    for d in range(v):
        shifted = [(s + d) % v for s in S]
        cnt = sum(1 for x in shifted if x <= 10000)
        if cnt == len(S):
            all_fit_count += 1
    print(f"Shifts preserving all {len(S)} elements: {all_fit_count}/{v}")
