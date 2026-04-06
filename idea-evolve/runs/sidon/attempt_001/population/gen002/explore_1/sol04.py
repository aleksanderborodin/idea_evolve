# fitness: TBD
# Construction: Randomized greedy + 1-opt swap, multiple restarts (time-limited)
# Different random orderings of {0..10000} give different local optima.
# Explores the solution space independently of ET algebraic structure.

import random
import time

def entrypoint():
    N = 10000
    time_limit = 25.0  # seconds
    t_start = time.time()

    def greedy_from_order(order):
        S = []
        used = set()
        for x in order:
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
                used.update(nd)
        return sorted(S), used

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

    def one_opt(S, used):
        """One round of 1-opt: remove each element, re-extend greedily, keep best."""
        best_S, best_used = S, used
        for i in range(len(S)):
            if time.time() - t_start > time_limit:
                return best_S, best_used
            x = S[i]
            S_new = S[:i] + S[i+1:]
            used_new = build_diffs(S_new)
            S_ext, used_ext = greedy_extend(S_new, used_new)
            if len(S_ext) > len(best_S):
                best_S = S_ext
                best_used = used_ext
        return best_S, best_used

    # Also seed with ET p=71 as one of the starting points
    p = 71
    et_base = sorted(2*p*k + k*k%p for k in range(1, p) if 2*p*k + k*k%p <= N)
    best_S, best_used = greedy_extend(et_base, build_diffs(et_base))
    best_S, best_used = one_opt(best_S, best_used)

    rng = random.Random(42)
    candidates = list(range(N + 1))

    restart = 0
    while time.time() - t_start < time_limit:
        restart += 1
        rng.shuffle(candidates)
        S, used = greedy_from_order(candidates)
        S, used = one_opt(S, used)
        if len(S) > len(best_S):
            best_S, best_used = S, used

    return best_S
