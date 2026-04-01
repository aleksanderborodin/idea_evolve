# fitness: TBD
"""
Singer difference set construction for Sidon sets.

For prime q=97: v = q^2+q+1 = 9507, Singer set has size q+1 = 98.
D is a (9507, 98, 1)-difference set: every non-zero difference mod 9507 appears exactly once.
This makes D a Sidon set of size 98 in {0, ..., 9506} ⊆ {0, ..., 10000}.

Construction:
  - GF(97^3) = GF(97)[x]/(x^3 + 2)  — irreducible over GF(97)
  - g = (5,1,0) is a primitive element of GF(97^3)* (order 912672 = 97^3-1)
  - Singer set D = {k in [0,9506] : g^k lies in hyperplane H = {(a,b,0)}}
    i.e., 3rd component of g^k equals 0
  - This gives exactly q+1 = 98 values, forming a (v,q+1,1)-difference set ≡ Sidon set
"""


def entrypoint():
    p = 97
    B, C = 0, 2  # Irreducible cubic x^3 + B*x + C = x^3 + 2 over GF(97)

    # GF(p^3) = GF(p)[x]/(x^3 + B*x + C)
    # Reduction: x^3 = -B*x - C = -2 (mod 97)
    def mul(u, v):
        u0, u1, u2 = u
        v0, v1, v2 = v
        w = [0] * 5
        for i, ui in enumerate([u0, u1, u2]):
            for j, vj in enumerate([v0, v1, v2]):
                w[i + j] += ui * vj
        # Reduce x^4 = -B*x^2 - C*x = -2x
        w[2] -= w[4] * B
        w[1] -= w[4] * C
        # Reduce x^3 = -B*x - C = -2
        w[1] -= w[3] * B
        w[0] -= w[3] * C
        return (w[0] % p, w[1] % p, w[2] % p)

    # g = (5,1,0) = 5 + x is a primitive element of GF(97^3)*, verified order = 97^3-1
    gen = (5, 1, 0)
    v = p * p + p + 1  # 9507 = q^2 + q + 1

    # Singer set: k in [0, v-1] where gen^k has zero 3rd component
    # This gives exactly q+1 = 98 elements forming a (v, q+1, 1)-difference set
    D = []
    identity = (1, 0, 0)
    current = identity
    for k in range(v):
        if current[2] == 0 and current != (0, 0, 0):
            D.append(k)
        current = mul(current, gen)

    return D
