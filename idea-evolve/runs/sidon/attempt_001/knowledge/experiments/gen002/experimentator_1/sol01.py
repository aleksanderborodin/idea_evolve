# fitness: 102
"""
Singer q=101 construction with optimal cyclic shift.

Uses find_singer_set(101) to get 102 elements in Z_{10303},
then applies cyclic shift 3538 which places ALL 102 elements
within {0..10000}. No truncation needed — every element fits.

This is a pure algebraic construction with no search component.
"""


def _find_irreducible_cubic(p):
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


def _prime_factors(n):
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


def _find_singer_set(q):
    v = q * q + q + 1
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

    def power(base, exp):
        result = (1, 0, 0)
        cur = base
        while exp > 0:
            if exp & 1:
                result = mul(result, cur)
            cur = mul(cur, cur)
            exp >>= 1
        return result

    v_full = q * q * q - 1
    factors = _prime_factors(v_full)

    gen = None
    for a in range(q):
        for b_coeff in range(q):
            candidate = (a, b_coeff, 0) if b_coeff > 0 else (a, 1, 0)
            if candidate == (0, 0, 0):
                continue
            ok = True
            for r in factors:
                if power(candidate, v_full // r) == (1, 0, 0):
                    ok = False
                    break
            if ok:
                gen = candidate
                break
        if gen is not None:
            break

    D = []
    current = (1, 0, 0)
    for k in range(v):
        if current[2] == 0 and current != (0, 0, 0):
            D.append(k)
        current = mul(current, gen)
    return sorted(D)


def entrypoint():
    q = 101
    v = q * q + q + 1  # 10303
    S = _find_singer_set(q)
    shift = 3538
    result = sorted([(s + shift) % v for s in S])
    return result
