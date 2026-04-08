# fitness: 75
"""
Enhanced Erdos-Turan construction with iterated local search.

Builds on the best known non-algebraic result (ET+greedy+1-opt = 75 from gen2).
Three improvements:
1. Systematic 2-opt: remove ALL pairs, extend greedily, keep best
2. Iterated large-neighborhood search: random perturbation + reextend
3. Try ET for primes p=67,71 and pick best starting point

The gen2 result was 75. Goal: push past that.
"""
import time
import random


def entrypoint():
    N = 10000
    TIME_LIMIT = 27.0
    start_t = time.time()
    best_ever = []

    # ---- Core utilities ----
    def build_used_diffs(S):
        used = set()
        for i in range(len(S)):
            for j in range(i + 1, len(S)):
                used.add(S[j] - S[i])
        return used

    def greedy_extend(S_base, used_base):
        """Extend S_base greedily through all [0..N] not in S_base."""
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

    def et_construction(p):
        """Erdos-Turan: S = {2pk + k²%p : k=0,...,p-1} filtered to [0,N]."""
        base = []
        for k in range(p):
            v = 2 * p * k + (k * k) % p
            if 0 <= v <= N:
                base.append(v)
        return sorted(set(base))

    def run_1opt(S):
        """1-opt: remove each element, re-extend greedily. Return best found."""
        best = list(S)
        improved = True
        while improved and time.time() - start_t < TIME_LIMIT - 0.5:
            improved = False
            for i in range(len(best)):
                if time.time() - start_t > TIME_LIMIT - 0.5:
                    break
                x = best[i]
                S_new = best[:i] + best[i+1:]
                used_new = build_used_diffs(S_new)
                S_ext, _ = greedy_extend(S_new, used_new)
                if len(S_ext) > len(best):
                    best = S_ext
                    improved = True
                    break
        return best

    def run_2opt(S):
        """2-opt: remove each pair, re-extend. Restart on improvement."""
        best = list(S)
        improved = True
        while improved and time.time() - start_t < TIME_LIMIT - 1.0:
            improved = False
            n = len(best)
            for i in range(n):
                if time.time() - start_t > TIME_LIMIT - 1.0:
                    return best
                for j in range(i + 1, n):
                    S_new = [best[k] for k in range(n) if k != i and k != j]
                    used_new = build_used_diffs(S_new)
                    S_ext, _ = greedy_extend(S_new, used_new)
                    if len(S_ext) > len(best):
                        best = S_ext
                        improved = True
                        if len(best) > len(best_ever):
                            pass  # will update after
                        break
                if improved:
                    break
        return best

    def random_perturbation(S, k_remove):
        """Remove k random elements from S, re-extend greedily."""
        if len(S) <= k_remove:
            return S
        indices = random.sample(range(len(S)), k_remove)
        S_new = [S[i] for i in range(len(S)) if i not in set(indices)]
        used_new = build_used_diffs(S_new)
        S_ext, _ = greedy_extend(S_new, used_new)
        return S_ext

    # ---- Phase 1: Build best ET base ----
    for p in [71, 67]:
        base = et_construction(p)
        used = build_used_diffs(base)
        S_ext, _ = greedy_extend(base, used)
        if len(S_ext) > len(best_ever):
            best_ever = S_ext

    # ---- Phase 2: 1-opt on best ----
    if time.time() - start_t < TIME_LIMIT - 2.0:
        best_ever = run_1opt(best_ever)

    # ---- Phase 3: 2-opt on best ----
    if time.time() - start_t < TIME_LIMIT - 3.0:
        candidate = run_2opt(best_ever)
        if len(candidate) > len(best_ever):
            best_ever = candidate

    # ---- Phase 4: Iterated large-neighborhood search ----
    # Remove k elements randomly, re-extend, 1-opt; repeat until time
    rng_seed = 42
    while time.time() - start_t < TIME_LIMIT - 0.5:
        random.seed(rng_seed)
        rng_seed += 1
        # Try removing 3, 5, 8 elements at random
        k = random.choice([3, 5, 8, 12])
        candidate = random_perturbation(best_ever, k)
        # Quick 1-opt on the candidate
        candidate = run_1opt(candidate)
        if len(candidate) > len(best_ever):
            best_ever = candidate

    # Fallback
    if len(best_ever) < 50:
        from helpers.search import greedy_sidon
        best_ever = greedy_sidon(range(N + 1))

    return sorted(best_ever)
