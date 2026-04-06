"""
Core helpers for the Sidon Sets problem.

A Sidon set (B2 sequence) is a set S where all pairwise sums a+b (a<=b) are distinct.
Equivalently, all positive differences are distinct.

These are utility functions — validation and number theory primitives.
"""

N_MAX = 10000


def is_sidon(S):
    """Check if S is a valid Sidon set."""
    S = sorted(set(S))
    sums = set()
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                return False
            sums.add(s)
    return True


def count_violations(S):
    """Count repeated pairwise sums."""
    S = sorted(set(S))
    sums = {}
    violations = 0
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                violations += 1
            else:
                sums[s] = True
    return violations


def differences(S):
    """Return the set of all positive differences."""
    S = sorted(set(S))
    diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            diffs.add(S[j] - S[i])
    return diffs


def can_add(S_sorted, used_diffs, candidate):
    """Check if candidate can be added to S without violating the Sidon property.
    S_sorted must be sorted. used_diffs is the set of existing differences.
    Returns (ok, new_diffs) where new_diffs is the set of new differences if ok."""
    new_diffs = set()
    for existing in S_sorted:
        d = abs(candidate - existing)
        if d in used_diffs or d in new_diffs:
            return False, set()
        new_diffs.add(d)
    return True, new_diffs


def is_prime(n):
    """Primality test."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def prime_factors(n):
    """Return set of prime factors of n."""
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors
