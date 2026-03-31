"""
Core helpers for Permutation Codes problem.

Usage:
    from helpers.core import hamming_distance, check_code, min_distance, pairwise_distances
"""

import numpy as np


def hamming_distance(p, q):
    """Hamming distance between two permutations (number of differing positions)."""
    p = np.asarray(p, dtype=int)
    q = np.asarray(q, dtype=int)
    return int(np.sum(p != q))


def min_distance(perms):
    """Minimum pairwise Hamming distance in a set of permutations.

    Args:
        perms: 2D array of shape (K, n), each row a permutation.

    Returns:
        int: minimum Hamming distance between any two distinct rows.
    """
    perms = np.asarray(perms, dtype=int)
    K = perms.shape[0]
    if K < 2:
        return perms.shape[1]  # vacuously maximum

    best = perms.shape[1]
    for i in range(K):
        dists = np.sum(perms[i] != perms[i + 1:], axis=1)
        if len(dists) > 0:
            best = min(best, int(np.min(dists)))
    return best


def check_code(perms, d):
    """Check if a permutation code is valid.

    Args:
        perms: 2D array of shape (K, n), each row a permutation.
        d: required minimum Hamming distance.

    Returns:
        (is_valid, code_size): tuple of (bool, int).
    """
    perms = np.asarray(perms, dtype=int)
    K, n = perms.shape
    expected = np.arange(n)

    # Check permutation validity
    for i in range(K):
        if not np.array_equal(np.sort(perms[i]), expected):
            return False, 0

    # Check uniqueness
    if len(set(map(tuple, perms))) < K:
        return False, 0

    # Check minimum distance
    if min_distance(perms) < d:
        return False, 0

    return True, K


def pairwise_distances(perms):
    """Compute all pairwise Hamming distances.

    Args:
        perms: 2D array of shape (K, n), each row a permutation.

    Returns:
        np.ndarray of shape (K, K): distance matrix.
    """
    perms = np.asarray(perms, dtype=int)
    K, n = perms.shape
    dist = np.zeros((K, K), dtype=int)
    for i in range(K):
        dist[i, i + 1:] = np.sum(perms[i] != perms[i + 1:], axis=1)
    dist += dist.T
    return dist


def compatible_permutations(perms, d, n=8):
    """Find all permutations of {0,...,n-1} compatible with a given code.

    A permutation p is compatible if hamming_distance(p, q) >= d for all q in perms.

    Args:
        perms: 2D array of shape (K, n), existing code.
        d: minimum Hamming distance.
        n: permutation length.

    Returns:
        np.ndarray of shape (M, n): all compatible permutations.
    """
    from itertools import permutations as iter_perms

    perms = np.asarray(perms, dtype=int)
    result = []

    for p in iter_perms(range(n)):
        p_arr = np.array(p, dtype=int)
        dists = np.sum(p_arr != perms, axis=1)
        if np.all(dists >= d):
            result.append(p_arr)

    if result:
        return np.array(result)
    return np.empty((0, n), dtype=int)
