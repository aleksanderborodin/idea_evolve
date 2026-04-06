"""Search and analysis helpers for Sidon set optimization.

Provides greedy construction and difference counting utilities
used by local search and analysis agents.

Usage:
    from helpers.search import greedy_sidon, build_diff_counts

    S = greedy_sidon(range(10001))        # baseline: 66 elements
    S = greedy_sidon(candidates, N=10000)  # from custom candidate order
    diffs = build_diff_counts(S)           # {diff: count} for analysis
"""


def greedy_sidon(candidates, N=10000):
    """Build the largest Sidon set by greedily selecting from candidates in order.

    For each candidate (in the given order), add it to the set if it doesn't
    create a repeated difference with existing elements. Maintains a set of
    used differences incrementally for O(|S|) per candidate check.

    Args:
        candidates: ordered iterable of candidate integers
        N: maximum allowed value (elements > N or < 0 are skipped)

    Returns:
        sorted list forming a valid Sidon set

    Examples:
        >>> len(greedy_sidon(range(10001)))
        66
        >>> from helpers.singer import find_singer_set
        >>> len(greedy_sidon(find_singer_set(97)))
        98
    """
    S = []
    used_diffs = set()
    for c in candidates:
        if c < 0 or c > N:
            continue
        new_diffs = set()
        ok = True
        for x in S:
            d = abs(c - x)
            if d in used_diffs or d in new_diffs:
                ok = False
                break
            new_diffs.add(d)
        if ok:
            S.append(c)
            used_diffs.update(new_diffs)
    return sorted(S)


def build_diff_counts(S):
    """Build a dictionary mapping each positive difference to its count.

    For a valid Sidon set, every value in the returned dict should be 1.
    For sets with violations, some values will be > 1.

    Useful for local search: after removing an element, decrement the counts
    of its differences to know which differences become free.

    Args:
        S: list of integers (typically a Sidon set)

    Returns:
        dict mapping each positive difference d to the number of pairs
        (i, j) with i < j such that S[j] - S[i] = d

    Examples:
        >>> d = build_diff_counts([0, 1, 3, 7])
        >>> all(v == 1 for v in d.values())
        True
        >>> len(d)  # C(4,2) = 6 unique differences
        6
    """
    S = sorted(S)
    counts = {}
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            d = S[j] - S[i]
            counts[d] = counts.get(d, 0) + 1
    return counts
