# fitness: 75
# Construction: ET p=71 + greedy + 1-opt swap local search
# For each element in the set: remove it, re-greedily extend. Accept if size improves.
# This "expansion move" explores whether removing a "blocker" allows 2 new elements.

def entrypoint():
    p = 71
    N = 10000

    def build_diffs(S):
        used = set()
        for i in range(len(S)):
            for j in range(i + 1, len(S)):
                used.add(S[j] - S[i])
        return used

    def greedy_extend(S, used):
        S = list(S)
        S_set = set(S)
        for x in range(N + 1):
            if x in S_set:
                continue
            nd = []
            ok = True
            for s in S:
                d = abs(x - s)
                if d in used or d in nd:
                    ok = False
                    break
                nd.append(d)
            if ok:
                S.append(x)
                S_set.add(x)
                used = used | set(nd)
        return sorted(S), used

    # Start with ET base
    base = sorted(2*p*k + k*k%p for k in range(1, p) if 2*p*k + k*k%p <= N)
    used = build_diffs(base)
    S, used = greedy_extend(base, used)

    improved = True
    while improved:
        improved = False
        for i in range(len(S)):
            x = S[i]
            # Remove x, recompute diffs
            S_new = S[:i] + S[i+1:]
            used_new = build_diffs(S_new)
            # Greedily extend
            S_ext, used_ext = greedy_extend(S_new, used_new)
            if len(S_ext) > len(S):
                S = S_ext
                used = used_ext
                improved = True
                break  # restart the loop

    return S
