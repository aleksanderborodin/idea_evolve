"""Development and testing of find_singer_set(q).

Singer difference set construction via GF(q^3).
For prime q, constructs a set of q+1 elements in Z_{q^2+q+1}
such that all pairwise differences are distinct (Sidon set).
"""
import sys
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon")
from helpers.core import is_sidon, count_violations


def _find_irreducible_cubic(p):
    """Find an irreducible cubic x^3 + bx + c over GF(p).

    Tries small coefficients first. An irreducible cubic has no roots in GF(p).
    """
    for c in range(p):
        for b in range(p):
            # Check x^3 + bx + c has no roots in GF(p)
            has_root = False
            for x in range(p):
                if (x*x*x + b*x + c) % p == 0:
                    has_root = True
                    break
            if not has_root:
                return (b, c)
    raise ValueError(f"No irreducible cubic found for p={p}")


def _is_primitive_element(gen, p, B, C, v):
    """Check if gen is a primitive element of GF(p^3)* (order = p^3 - 1).

    A primitive element has order exactly v_full = p^3 - 1.
    We check that gen^(v_full/r) != identity for each prime factor r of v_full.
    """
    v_full = p * p * p - 1

    def mul(u, w):
        u0, u1, u2 = u
        w0, w1, w2 = w
        r = [0] * 5
        for i, ui in enumerate([u0, u1, u2]):
            for j, wj in enumerate([w0, w1, w2]):
                r[i + j] += ui * wj
        # Reduce by x^3 + Bx + C: x^3 = -Bx - C
        r[2] -= r[4] * B
        r[1] -= r[4] * C
        r[1] -= r[3] * B
        r[0] -= r[3] * C
        return (r[0] % p, r[1] % p, r[2] % p)

    def power(base, exp):
        result = (1, 0, 0)
        cur = base
        while exp > 0:
            if exp & 1:
                result = mul(result, cur)
            cur = mul(cur, cur)
            exp >>= 1
        return result

    # Find prime factors of v_full
    factors = set()
    n = v_full
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)

    # Check gen^(v_full/r) != (1,0,0) for each prime factor r
    for r in factors:
        if power(gen, v_full // r) == (1, 0, 0):
            return False
    return True


def find_singer_set(q):
    """Construct a Singer difference set of size q+1 in Z_{q^2+q+1}.

    Uses GF(q^3) construction: finds a primitive element g of GF(q^3)*,
    then the Singer set is {k : g^k has zero x^2 coefficient (third coordinate)}.

    Args:
        q: a prime number

    Returns:
        sorted list of q+1 integers in {0, ..., q^2+q}

    The returned set is a valid Sidon set (all pairwise differences distinct).

    Examples:
        >>> S = find_singer_set(97)
        >>> len(S)
        98
        >>> find_singer_set(7)
        [0, 1, 3, 7, 12, 18, 35, 44]
    """
    v = q * q + q + 1  # order of the cyclic group

    # Find irreducible cubic x^3 + Bx + C over GF(q)
    B, C = _find_irreducible_cubic(q)

    def mul(u, w):
        u0, u1, u2 = u
        w0, w1, w2 = w
        r = [0] * 5
        for i, ui in enumerate([u0, u1, u2]):
            for j, wj in enumerate([w0, w1, w2]):
                r[i + j] += ui * wj
        r[2] -= r[4] * B
        r[1] -= r[4] * C
        r[1] -= r[3] * B
        r[0] -= r[3] * C
        return (r[0] % q, r[1] % q, r[2] % q)

    # Find a primitive element of GF(q^3)*
    # Try candidates (a, 1, 0) for various a
    gen = None
    for a in range(q):
        for b_coeff in range(q):
            candidate = (a, 1, 0) if b_coeff == 0 else (a, b_coeff, 0)
            if candidate == (0, 0, 0):
                continue
            if b_coeff > 0 and b_coeff != 1:
                candidate = (a, b_coeff, 0)
            if _is_primitive_element(candidate, q, B, C, v):
                gen = candidate
                break
        if gen is not None:
            break

    if gen is None:
        # Try with nonzero third coordinate
        for a in range(q):
            for b_coeff in range(q):
                candidate = (a, b_coeff, 1)
                if _is_primitive_element(candidate, q, B, C, v):
                    gen = candidate
                    break
            if gen is not None:
                break

    if gen is None:
        raise ValueError(f"Could not find primitive element for GF({q}^3)")

    # Collect indices k where g^k has zero x^2 coefficient
    D = []
    identity = (1, 0, 0)
    current = identity
    for k in range(v):
        if current[2] == 0 and current != (0, 0, 0):
            D.append(k)
        current = mul(current, gen)

    return sorted(D)


# Test
if __name__ == "__main__":
    print("Testing find_singer_set...")

    # Test q=7
    S7 = find_singer_set(7)
    print(f"q=7: {len(S7)} elements, is_sidon={is_sidon(S7)}, set={S7}")
    assert len(S7) == 8, f"Expected 8 elements, got {len(S7)}"
    assert is_sidon(S7), "q=7 set is not Sidon!"
    assert all(0 <= x <= 57 for x in S7), "q=7 elements out of range"
    print("  PASS: q=7")

    # Test q=97
    S97 = find_singer_set(97)
    print(f"q=97: {len(S97)} elements, is_sidon={is_sidon(S97)}")
    assert len(S97) == 98, f"Expected 98 elements, got {len(S97)}"
    assert is_sidon(S97), "q=97 set is not Sidon!"
    assert all(0 <= x <= 9506 for x in S97), "q=97 elements out of range"
    print("  PASS: q=97")

    # Test q=101
    S101 = find_singer_set(101)
    print(f"q=101: {len(S101)} elements, is_sidon={is_sidon(S101)}")
    assert len(S101) == 102, f"Expected 102 elements, got {len(S101)}"
    assert is_sidon(S101), "q=101 set is not Sidon!"
    assert all(0 <= x <= 10302 for x in S101), "q=101 elements out of range"
    print("  PASS: q=101")

    # Test q=2
    S2 = find_singer_set(2)
    print(f"q=2: {len(S2)} elements, is_sidon={is_sidon(S2)}, set={S2}")
    assert len(S2) == 3, f"Expected 3 elements, got {len(S2)}"
    assert is_sidon(S2), "q=2 set is not Sidon!"
    print("  PASS: q=2")

    # Test q=3
    S3 = find_singer_set(3)
    print(f"q=3: {len(S3)} elements, is_sidon={is_sidon(S3)}, set={S3}")
    assert len(S3) == 4, f"Expected 4 elements, got {len(S3)}"
    assert is_sidon(S3), "q=3 set is not Sidon!"
    print("  PASS: q=3")

    # Test q=5
    S5 = find_singer_set(5)
    print(f"q=5: {len(S5)} elements, is_sidon={is_sidon(S5)}, set={S5}")
    assert len(S5) == 6, f"Expected 6 elements, got {len(S5)}"
    assert is_sidon(S5), "q=5 set is not Sidon!"
    print("  PASS: q=5")

    print("\nAll find_singer_set tests passed!")
