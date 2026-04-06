# fitness: TBD
"""
Singer q=103 difference set — 104 elements in {0,...,10000}.

Based on Rokicki-Dogon "Possibly Optimal Golomb Rulers" database:
- 104 marks, span=9581, type=pp (projective plane / Singer), q=103
- This guarantees a cyclic rotation of Singer(103) fits within {0,...,9581} ⊂ {0,...,10000}

Singer(103) = perfect difference set of 104 elements in Z_{10713}
"""
import sys
import os

# Add problem dir to path for helpers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'problem'))
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon')

from helpers.singer import find_singer_set


def find_optimal_shift(D, v, N=10000):
    """Find cyclic shift of difference set D (in Z_v) that minimizes max element.

    For each element d in D, try shifting so d maps to 0 (i.e., subtract d mod v).
    Returns the shifted set if all elements fit in {0,...,N}, else None.

    Guaranteed to succeed if the minimum span of D is <= N.
    """
    best_set = None
    best_max = v + 1

    for anchor in D:
        shifted = sorted([(x - anchor) % v for x in D])
        max_elem = shifted[-1]
        if max_elem <= N and max_elem < best_max:
            best_max = max_elem
            best_set = shifted

    return best_set


def entrypoint():
    q = 103
    v = q * q + q + 1  # = 10713 (modulus for Singer set)
    N = 10000

    # Build Singer difference set for q=103: 104 elements in Z_{10713}
    D = find_singer_set(q)
    assert len(D) == q + 1, f"Expected {q+1} elements, got {len(D)}"

    # Find cyclic rotation with all elements <= N
    result = find_optimal_shift(D, v, N)

    if result is not None:
        return result

    # Fallback: if no single-anchor rotation works perfectly,
    # find the rotation with fewest elements > N and drop those
    best_truncated = None
    best_count = 0
    for anchor in D:
        shifted = sorted([(x - anchor) % v for x in D])
        within = [x for x in shifted if x <= N]
        if len(within) > best_count:
            best_count = len(within)
            best_truncated = within

    return best_truncated if best_truncated else D[:q]
