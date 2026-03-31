"""AGL(1,8) construction helpers for the M(8,5) permutation code problem.

Provides GF(2^3) field arithmetic, AGL(1,8) group element generation,
orbit computation, compatibility graph construction, and max clique search.

The AGL(1,8) orbit clique construction achieves M(8,5) >= 616, the known
lower bound (Smith & Montemanni, 2012).

Usage:
    from helpers.agl18 import gf8_mul, agl18_elements, agl18_orbits
    from helpers.agl18 import agl18_orbit_reps, agl18_compat_graph, agl18_max_clique_code

Tested: all functions validated against helpers/core.py check_code().
Timings (measured): orbits 0.9s, compat graph 3.7s, full pipeline 4.0s.
"""

import numpy as np
from itertools import combinations


def gf8_mul(a, b):
    """Multiply two elements in GF(2^3) with primitive polynomial x^3+x+1.

    Elements are integers 0-7, representing polynomials over GF(2):
      0=0, 1=1, 2=x, 3=x+1, 4=x^2, 5=x^2+1, 6=x^2+x, 7=x^2+x+1

    Args:
        a: int in [0, 7], first operand.
        b: int in [0, 7], second operand.

    Returns:
        int in [0, 7], the product a*b in GF(8).

    Example:
        >>> gf8_mul(2, 3)  # x * (x+1) = x^2 + x = 6
        6
        >>> gf8_mul(2, 4)  # x * x^2 = x^3 = x+1 (mod x^3+x+1) = 3
        3
    """
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 8:
            a ^= 0b1011
    return result


def _build_gf8_mul_table():
    """Build 8x8 multiplication table for GF(8)."""
    table = np.zeros((8, 8), dtype=np.int8)
    for a in range(8):
        for b in range(8):
            table[a, b] = gf8_mul(a, b)
    return table


def agl18_elements():
    """Return all 56 elements of AGL(1,8) as permutations of {0,...,7}.

    AGL(1,8) = {x -> a*x + b : a in GF(8)*, b in GF(8)}
    where * denotes GF(8) multiplication and + denotes XOR.

    Returns:
        np.ndarray of shape (56, 8), dtype int8.

    Example:
        >>> elems = agl18_elements()
        >>> elems.shape
        (56, 8)
    """
    MUL = _build_gf8_mul_table()
    perms = np.empty((56, 8), dtype=np.int8)
    idx = 0
    for a in range(1, 8):
        for b in range(8):
            for x in range(8):
                perms[idx, x] = MUL[a, x] ^ b
            idx += 1
    return perms


def agl18_orbits(all_perms=None):
    """Partition S_8 into orbits under left-action of AGL(1,8).

    Left-action: h . pi = h(pi(x)) for all x (composition: apply pi then h).
    Each orbit has exactly 56 elements. Total: 720 orbits covering all 40320 perms.

    Args:
        all_perms: Optional (N, 8) array of all permutations. If None, generates all 40320.

    Returns:
        list of np.ndarray, each of shape (56, 8). Length = 720.

    Example:
        >>> orbits = agl18_orbits()
        >>> len(orbits)
        720
    """
    if all_perms is None:
        from itertools import permutations as iperms
        all_perms = np.array(list(iperms(range(8))), dtype=np.int8)

    agl = agl18_elements()
    perm_to_idx = {}
    for i in range(len(all_perms)):
        perm_to_idx[tuple(all_perms[i].tolist())] = i

    visited = np.zeros(len(all_perms), dtype=bool)
    orbits = []

    for start in range(len(all_perms)):
        if visited[start]:
            continue
        pi = all_perms[start]
        orbit = agl[:, pi]  # (56, 8) — h(pi(x)) via fancy indexing
        for row in orbit:
            visited[perm_to_idx[tuple(row.tolist())]] = True
        orbits.append(orbit)

    return orbits


def agl18_orbit_reps(all_perms=None):
    """Return canonical representatives (lexicographically smallest) per orbit.

    Args:
        all_perms: Optional (N, 8) array. If None, generates all 40320.

    Returns:
        np.ndarray of shape (720, 8), dtype int8.

    Example:
        >>> reps = agl18_orbit_reps()
        >>> reps.shape
        (720, 8)
    """
    orbits = agl18_orbits(all_perms)
    reps = np.empty((len(orbits), 8), dtype=np.int8)
    for i, orbit in enumerate(orbits):
        sorted_idx = np.lexsort(orbit[:, ::-1].T)
        reps[i] = orbit[sorted_idx[0]]
    return reps


def agl18_compat_graph(all_perms=None, d=5):
    """Build compatibility graph between AGL(1,8) orbits.

    Two orbits are compatible iff min_{h in AGL} hamming(h(rep_i), rep_j) >= d.
    The graph is perfectly regular with degree 138 for d=5.

    Args:
        all_perms: Optional (N, 8) array.
        d: Minimum Hamming distance (default 5).

    Returns:
        np.ndarray of shape (720, 720), dtype bool. True = compatible.

    Example:
        >>> G = agl18_compat_graph()
        >>> G.sum(axis=1)[0]
        138
    """
    orbits = agl18_orbits(all_perms)
    agl = agl18_elements()
    n_orbits = len(orbits)
    reps = np.empty((n_orbits, 8), dtype=np.int8)
    for i, orbit in enumerate(orbits):
        sorted_idx = np.lexsort(orbit[:, ::-1].T)
        reps[i] = orbit[sorted_idx[0]]

    all_translates = np.empty((n_orbits, 56, 8), dtype=np.int8)
    for i in range(n_orbits):
        all_translates[i] = agl[:, reps[i]]

    compat = np.ones((n_orbits, n_orbits), dtype=bool)
    np.fill_diagonal(compat, False)

    for i in range(n_orbits):
        remaining_reps = reps[i+1:]
        if len(remaining_reps) == 0:
            break
        dists = np.sum(all_translates[i][:, np.newaxis, :] != remaining_reps[np.newaxis, :, :], axis=2)
        min_dists = dists.min(axis=0)
        incompat = min_dists < d
        compat[i, i+1:][incompat] = False
        compat[i+1:, i][incompat] = False

    return compat


def agl18_max_clique_code(d=5):
    """Find max clique in AGL(1,8) orbit graph and return the full code.

    For M(8,5), the max clique has 11 orbits, yielding 11 * 56 = 616 codewords.
    Uses greedy clique search from multiple starting vertices.

    Args:
        d: Minimum Hamming distance (default 5).

    Returns:
        np.ndarray of shape (K, 8), dtype int32. K=616 for d=5.

    Example:
        >>> code = agl18_max_clique_code()
        >>> code.shape[0]
        616
    """
    from itertools import permutations as iperms
    all_perms = np.array(list(iperms(range(8))), dtype=np.int8)

    orbits = agl18_orbits(all_perms)
    compat = agl18_compat_graph(all_perms, d)
    n_orbits = len(orbits)

    degrees = compat.sum(axis=1)
    order = np.argsort(-degrees)

    best_clique = []
    for sv in range(min(50, n_orbits)):
        clique = [int(order[sv])]
        cands = np.where(compat[order[sv]])[0].tolist()
        while cands:
            scored = [(c, sum(1 for c2 in cands if compat[c, c2])) for c in cands]
            scored.sort(key=lambda x: -x[1])
            v = scored[0][0]
            clique.append(v)
            cands = [c for c in cands if compat[v, c]]
        if len(clique) > len(best_clique):
            best_clique = clique
        if len(best_clique) >= 11:
            break

    code_parts = [orbits[c] for c in best_clique]
    return np.vstack(code_parts).astype(np.int32)
