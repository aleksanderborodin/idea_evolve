"""Singer difference set construction via GF(q^3).

For prime q, constructs a Sidon set of q+1 elements in Z_{q^2+q+1}
using the classical Singer construction over finite fields.

Usage:
    from helpers.singer import find_singer_set

    S = find_singer_set(97)   # 98 elements in {0..9506}
    S = find_singer_set(101)  # 102 elements in {0..10302}
"""


def _find_irreducible_cubic(p):
    """Find an irreducible cubic x^3 + bx + c over GF(p).

    Returns (b, c) such that x^3 + bx + c has no roots in GF(p).
    """
    for c in range(p):
        for b in range(p):
            has_root = False
            for x in range(p):
                if (x * x * x + b * x + c) % p == 0:
                    has_root = True
                    break
            if not has_root:
                return (b, c)
    raise ValueError(f"No irreducible cubic found for p={p}")


def _is_primitive_element(gen, p, B, C):
    """Check if gen is a primitive element of GF(p^3)* (order = p^3 - 1).

    Verifies gen^((p^3-1)/r) != 1 for each prime factor r of p^3 - 1.
    """
    v_full = p * p * p - 1

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

    # Prime factors of v_full
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

    for r in factors:
        if power(gen, v_full // r) == (1, 0, 0):
            return False
    return True


def find_singer_set(q):
    """Construct a Singer difference set of size q+1 in Z_{q^2+q+1}.

    Uses GF(q^3) construction: finds a primitive element g of GF(q^3)*,
    then collects indices k where g^k has zero x^2 coefficient.

    Args:
        q: a prime number

    Returns:
        sorted list of q+1 integers in {0, ..., q^2+q}

    The returned set is a valid Sidon set (all pairwise differences distinct).

    Examples:
        >>> S = find_singer_set(97)
        >>> len(S)
        98
        >>> S = find_singer_set(7)
        >>> len(S)
        8
    """
    v = q * q + q + 1

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
    gen = None
    for a in range(q):
        for b_coeff in range(q):
            candidate = (a, b_coeff, 0) if b_coeff > 0 else (a, 1, 0)
            if candidate == (0, 0, 0):
                continue
            if _is_primitive_element(candidate, q, B, C):
                gen = candidate
                break
        if gen is not None:
            break

    if gen is None:
        # Try with nonzero third coordinate
        for a in range(q):
            for b_coeff in range(q):
                candidate = (a, b_coeff, 1)
                if _is_primitive_element(candidate, q, B, C):
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
