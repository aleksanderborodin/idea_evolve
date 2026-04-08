# fitness: 75
"""
ET + Aggressive LNS to push past 75.

Strategy:
1. ET(71)+greedy+1-opt gets to 75 quickly (~2s)
2. Use remaining 25s for large-neighborhood search:
   - Randomly remove 2, 3, 4, 5 elements at a time
   - Re-extend greedily
   - Apply 1-opt on result
   - Accept if improvement

Key insight: 1-opt converges to local optimum at 75. LNS escapes by removing
multiple elements (larger perturbation), potentially landing in a basin with
a higher local optimum.
"""
import time
import random


def entrypoint():
    N = 10000
    TIME_LIMIT = 27.0
    start_t = time.time()

    def build_used(S):
        used = set()
        for i in range(len(S)):
            for j in range(i + 1, len(S)):
                used.add(S[j] - S[i])
        return used

    def greedy_ext(S_base, used_base):
        S = list(S_base)
        S_set = set(S)
        used = set(used_base)
        for x in range(N + 1):
            if x in S_set:
                continue
            nd = set()
            ok = True
            for s in S:
                d = abs(x - s)
                if d in used or d in nd:
                    ok = False
                    break
                nd.add(d)
            if ok:
                S.append(x)
                S_set.add(x)
                used.update(nd)
        return sorted(S), used

    def one_opt(S):
        """1-opt with incremental diff removal (avoids O(n²) rebuild)."""
        best = list(S)
        best_used = build_used(best)
        improved = True
        while improved and time.time() - start_t < TIME_LIMIT - 0.5:
            improved = False
            for i in range(len(best)):
                if time.time() - start_t > TIME_LIMIT - 0.5:
                    return best
                x = best[i]
                # Incrementally compute used_diffs without x (valid since Sidon = unique diffs)
                freed = set(abs(x - best[j]) for j in range(len(best)) if j != i)
                used_without = best_used - freed
                S_without = best[:i] + best[i+1:]
                S_ext, new_used = greedy_ext(S_without, used_without)
                if len(S_ext) > len(best):
                    best = S_ext
                    best_used = new_used
                    improved = True
                    break
        return best

    # ---- Phase 1: Initial construction ----
    def et_base(p):
        base = []
        for k in range(p):
            v = 2 * p * k + (k * k) % p
            if 0 <= v <= N:
                base.append(v)
        return sorted(set(base))

    base71 = et_base(71)
    used71 = build_used(base71)
    S0, _ = greedy_ext(base71, used71)

    # 1-opt to local optimum
    best = one_opt(S0)

    # ---- Phase 2: LNS with random perturbations ----
    # Targeted LNS: try removing 2-6 elements, re-extend, 1-opt
    seed = 0
    no_improve_count = 0

    while time.time() - start_t < TIME_LIMIT - 0.5:
        random.seed(seed)
        seed += 1

        # Vary removal size based on how stuck we are
        if no_improve_count < 10:
            k = random.choice([2, 2, 3])
        elif no_improve_count < 25:
            k = random.choice([3, 4, 5])
        else:
            k = random.choice([5, 8, 10, 15])

        k = min(k, len(best) - 10)

        indices = sorted(random.sample(range(len(best)), k))
        S_new = [best[i] for i in range(len(best)) if i not in set(indices)]
        used_new = build_used(S_new)
        S_ext, _ = greedy_ext(S_new, used_new)

        # Quick 1-opt only if we have time
        if time.time() - start_t < TIME_LIMIT - 3.0:
            S_ext = one_opt(S_ext)

        if len(S_ext) > len(best):
            best = S_ext
            no_improve_count = 0
        else:
            no_improve_count += 1

    return sorted(best)
