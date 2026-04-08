# fitness: 75
"""
Randomized greedy with 1-opt, many independent restarts.

Key experiment: how many distinct local optima are reachable in 27s?
Does randomized starting ever land above 75?

Each restart:
1. Shuffle candidate order
2. Greedy construction
3. Quick 1-opt (limited passes)

Also explores: ET construction with random perturbation of base.
"""
import time
import random


def entrypoint():
    N = 10000
    TIME_LIMIT = 27.0
    start_t = time.time()
    best = []
    rng = random.Random(0)

    def build_used(S):
        used = set()
        for i in range(len(S)):
            for j in range(i + 1, len(S)):
                used.add(S[j] - S[i])
        return used

    def greedy_build(order):
        """Build Sidon set from candidates in given order."""
        S = []
        used = set()
        for c in order:
            if c < 0 or c > N:
                continue
            nd = set()
            ok = True
            for x in S:
                d = abs(c - x)
                if d in used or d in nd:
                    ok = False
                    break
                nd.add(d)
            if ok:
                S.append(c)
                used.update(nd)
        return sorted(S), used

    def quick_1opt(S, max_passes=3):
        """1-opt with limited passes for speed."""
        best = list(S)
        best_used = build_used(best)

        for _ in range(max_passes):
            if time.time() - start_t > TIME_LIMIT - 0.5:
                break
            improved = False
            for i in range(len(best)):
                if time.time() - start_t > TIME_LIMIT - 0.5:
                    return best
                x = best[i]
                # Incremental diff removal (valid for Sidon sets)
                freed = set(abs(x - best[j]) for j in range(len(best)) if j != i)
                used_without = best_used - freed
                S_without = best[:i] + best[i+1:]

                # Greedy extend
                S2 = list(S_without)
                S2_set = set(S2)
                used2 = set(used_without)
                for c in range(N + 1):
                    if c in S2_set:
                        continue
                    nd = set()
                    ok = True
                    for s in S2:
                        d = abs(c - s)
                        if d in used2 or d in nd:
                            ok = False
                            break
                        nd.add(d)
                    if ok:
                        S2.append(c)
                        S2_set.add(c)
                        used2.update(nd)

                if len(S2) > len(best):
                    best = sorted(S2)
                    best_used = used2
                    improved = True
                    break  # restart this pass

            if not improved:
                break

        return best

    def et_base(p):
        base = sorted(set(
            2 * p * k + (k * k) % p
            for k in range(p)
            if 2 * p * k + (k * k) % p <= N
        ))
        return base

    # ---- Phase 1: ET(71) start ----
    base71 = et_base(71)
    used71 = build_used(base71)
    S0 = list(base71)
    S0_set = set(S0)
    used_s0 = set(used71)
    for c in range(N + 1):
        if c in S0_set:
            continue
        nd = set()
        ok = True
        for s in S0:
            d = abs(c - s)
            if d in used_s0 or d in nd:
                ok = False
                break
            nd.add(d)
        if ok:
            S0.append(c)
            S0_set.add(c)
            used_s0.update(nd)
    S0 = sorted(S0)
    best = quick_1opt(S0, max_passes=10)

    # ---- Phase 2: Randomized greedy restarts ----
    seed = 0
    while time.time() - start_t < TIME_LIMIT - 1.0:
        rng = random.Random(seed)
        seed += 1

        # Either: random order, or ET base + random extension
        mode = seed % 3
        if mode == 0:
            # Fully random order
            order = list(range(N + 1))
            rng.shuffle(order)
            S, _ = greedy_build(order)
        elif mode == 1:
            # ET base with random ordering of non-base elements
            base = et_base(71)
            non_base = [x for x in range(N + 1) if x not in set(base)]
            rng.shuffle(non_base)
            order = base + non_base  # ET elements first, then random fill
            S, _ = greedy_build(order)
        else:
            # ET base, remove 1-3 random elements, random re-extension
            base = et_base(71)
            k = rng.randint(1, 5)
            if k < len(base):
                indices = rng.sample(range(len(base)), k)
                base_mod = [base[i] for i in range(len(base)) if i not in set(indices)]
            else:
                base_mod = base
            non_base = [x for x in range(N + 1) if x not in set(base_mod)]
            rng.shuffle(non_base)
            order = base_mod + non_base
            S, _ = greedy_build(order)

        # Apply quick 1-opt
        if time.time() - start_t < TIME_LIMIT - 3.0:
            S = quick_1opt(S, max_passes=2)

        if len(S) > len(best):
            best = S

    return sorted(best)
