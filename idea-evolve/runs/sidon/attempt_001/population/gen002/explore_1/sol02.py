# fitness: 74
# Construction: Erdős-Turán p=71 + greedy extension over all {0..10000}
# Base: 70 elements. Greedy scans all candidates (not just unused range) to add more.

def entrypoint():
    p = 71
    S = sorted(2 * p * k + (k * k % p) for k in range(1, p) if 2*p*k + k*k%p <= 10000)

    used_diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            used_diffs.add(S[j] - S[i])

    S_set = set(S)
    for x in range(10001):
        if x in S_set:
            continue
        new_diffs = []
        ok = True
        for s in S:
            d = abs(x - s)
            if d in used_diffs or d in new_diffs:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            S.append(x)
            S.sort()
            used_diffs.update(new_diffs)
            S_set.add(x)

    return S
