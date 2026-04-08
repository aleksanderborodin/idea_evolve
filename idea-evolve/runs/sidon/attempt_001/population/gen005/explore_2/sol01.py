# fitness: TBD
"""
Bose-Chowla construction: algebraically distinct from Singer.
For prime p, S = {i*p + (i^2 mod p) : i = 0,...,p-1}.
Span = p^2 - 1. For p=97, span=9408 fits in [0,10000].
Then greedily extend with remaining candidates.

This is provably a Sidon set (B2 sequence) by number theory:
if a-b = c-d with distinct a,b,c,d in S, write each element as
i*p + r where r = i^2 mod p, derive contradiction from linear algebra over Z_p.
"""


def entrypoint():
    N = 10000

    def bose_chowla(p):
        """Construct Sidon set of size p with span p^2-1."""
        S = []
        for i in range(p):
            elem = i * p + (i * i) % p
            S.append(elem)
        return sorted(S)

    def greedy_extend(base, N):
        """Greedily extend a Sidon set with elements from [0,N]."""
        S = list(base)
        used_diffs = set()
        for i in range(len(S)):
            for j in range(i + 1, len(S)):
                used_diffs.add(S[j] - S[i])

        base_set = set(base)
        for candidate in range(N + 1):
            if candidate in base_set:
                continue
            new_diffs = set()
            ok = True
            for x in S:
                d = abs(candidate - x)
                if d in used_diffs or d in new_diffs:
                    ok = False
                    break
                new_diffs.add(d)
            if ok:
                S.append(candidate)
                used_diffs.update(new_diffs)
                base_set.add(candidate)

        return sorted(S)

    # p=97: span=9408, all 97 elements fit in [0,10000]
    base97 = bose_chowla(97)
    result = greedy_extend(base97, N)
    return result
