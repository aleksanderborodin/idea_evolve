"""Optimal cyclic shift and blocker analysis for Singer difference sets.

Given a Singer set in Z_v (from find_singer_set), finds the cyclic shift
that maximizes elements fitting in {0, ..., N}. Also provides blocker
analysis to understand why a set is saturated (cannot be extended).

Usage:
    from helpers.optimal_shift import find_optimal_shift, analyze_blockers
    from helpers.singer import find_singer_set

    S = find_singer_set(101)
    v = 101**2 + 101 + 1
    best_shift, truncated = find_optimal_shift(S, v)
    # truncated is a sorted list of 102 elements in {0, ..., 10000}

    blockers = analyze_blockers(truncated)
    # blockers[c] = number of members blocking non-member c
"""


def find_optimal_shift(singer_set, v, N=10000):
    """
    Given a Singer set in Z_v, find the cyclic shift d that maximizes
    the number of elements in {0, ..., N}.

    Tries all v possible shifts and returns the one that keeps the most
    elements in range. For q=101, this finds a shift preserving all 102
    elements. For q=103 (v=10713), the best shift keeps 102 of 104.

    Args:
        singer_set: list of integers in Z_v (the raw Singer set)
        v: the modulus (q^2 + q + 1)
        N: upper bound of target range (default 10000)

    Returns:
        (best_shift, truncated_set) where truncated_set is the sorted list
        of elements in {0, ..., N} after applying the best shift.

    Examples:
        >>> from helpers.singer import find_singer_set
        >>> S = find_singer_set(101)
        >>> shift, trunc = find_optimal_shift(S, 10303)
        >>> len(trunc)
        102
        >>> S = find_singer_set(97)
        >>> shift, trunc = find_optimal_shift(S, 9507)
        >>> len(trunc)
        98
        >>> S = find_singer_set(103)
        >>> shift, trunc = find_optimal_shift(S, 10713)
        >>> len(trunc)
        102
    """
    best_shift = 0
    best_count = 0
    best_set = []

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
    appears as a difference between two existing members. Each such x is one
    "blocker". To add c to the set, ALL its blockers would need to be removed
    first — so the blocker count is a lower bound on the disruption needed.

    For the q=101 Singer truncation (102 elements), minimum blockers = 45.
    This proves the set is deeply saturated: no local search can extend it.

    Args:
        sidon_set: list of integers forming a valid Sidon set
        N: upper bound of range (default 10000)

    Returns:
        dict mapping each non-member in {0,...,N} to its blocker count.
        Higher count = harder to add this element.

    Examples:
        >>> blockers = analyze_blockers([0, 1, 3], N=6)
        >>> blockers[2]  # blocked by all 3 members
        3
        >>> blockers[5]  # blocked by only 1 member
        1
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
