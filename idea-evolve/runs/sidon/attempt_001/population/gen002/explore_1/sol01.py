# fitness: 70
# Construction: Erdős-Turán (1941) — {2pk + k^2 mod p : k=1..p-1}, p=71
# Gives 70 elements in {143..9941}. Proven Sidon: spacing 2p prevents carry violations.
# Completely different from Singer/GF(q^3). Verified zero violations for this formula.

def entrypoint():
    p = 71
    S = []
    for k in range(1, p):
        elem = 2 * p * k + (k * k % p)
        if elem <= 10000:
            S.append(elem)
    return S
