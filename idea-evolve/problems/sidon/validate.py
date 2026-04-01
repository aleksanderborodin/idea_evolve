"""
Validate a candidate Sidon set.

Input: list of integers (returned by entrypoint())
Process: check range, check Sidon property, extract largest valid subset if needed.
Output: dict with fitness (set size), violations, is_valid.
"""

N_MAX = 10000


def _count_violations(S):
    """Count the number of repeated pairwise sums."""
    sums = {}
    violations = 0
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                violations += 1
            else:
                sums[s] = (i, j)
    return violations


def _is_sidon(S):
    """Check if S is a valid Sidon set (all pairwise sums distinct)."""
    return _count_violations(S) == 0


def _extract_largest_sidon_subset(S):
    """Greedy extraction: keep elements that don't create violations.
    Tries multiple orderings and returns the largest result."""
    best = []

    # Try original order
    best = _greedy_extract(S)

    # Try reverse order
    candidate = _greedy_extract(S[::-1])
    if len(candidate) > len(best):
        best = candidate

    # Try sorted order
    candidate = _greedy_extract(sorted(S))
    if len(candidate) > len(best):
        best = candidate

    # Try sorted descending
    candidate = _greedy_extract(sorted(S, reverse=True))
    if len(candidate) > len(best):
        best = candidate

    return sorted(best)


def _greedy_extract(S):
    """Greedy: add elements one by one, skip if they'd create a repeated sum."""
    result = []
    used_sums = set()
    for x in S:
        # Check if adding x creates any repeated sum
        new_sums = set()
        conflict = False
        for y in result:
            s = x + y
            if s in used_sums:
                conflict = True
                break
            new_sums.add(s)
        # Also check x + x
        s_self = x + x
        if s_self in used_sums:
            conflict = True
        else:
            new_sums.add(s_self)

        if not conflict:
            result.append(x)
            used_sums.update(new_sums)
    return result


def validate(S):
    """
    Validate a Sidon set candidate.

    Args:
        S: list of integers — the candidate Sidon set

    Returns:
        dict with fitness (size of largest valid Sidon subset), violations, is_valid, raw_size
    """
    if not isinstance(S, (list, tuple)):
        raise ValueError(f"entrypoint() must return a list of integers, got {type(S).__name__}")

    if len(S) == 0:
        raise ValueError("Empty set returned")

    # Convert to list of ints, filter to valid range
    try:
        S = [int(x) for x in S]
    except (TypeError, ValueError) as e:
        raise ValueError(f"All elements must be integers: {e}")

    # Remove duplicates (preserve order)
    seen = set()
    unique = []
    for x in S:
        if x not in seen and 0 <= x <= N_MAX:
            seen.add(x)
            unique.append(x)
    S = unique

    if len(S) == 0:
        raise ValueError("No valid elements in range [0, 10000]")

    raw_size = len(S)
    violations = _count_violations(S)

    if violations == 0:
        # Perfect Sidon set
        return {
            "fitness": len(S),
            "is_valid": 1,
            "violations": 0,
            "raw_size": raw_size,
        }
    else:
        # Has violations — extract largest valid subset
        valid_subset = _extract_largest_sidon_subset(S)
        return {
            "fitness": len(valid_subset),
            "is_valid": 0,
            "violations": violations,
            "raw_size": raw_size,
        }
