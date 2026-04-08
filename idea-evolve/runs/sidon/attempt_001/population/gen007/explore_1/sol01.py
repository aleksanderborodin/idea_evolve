# fitness: 74
# approach: Ruzsa-Lindstrom (primitive root) construction p=71 with 2p scaling
# S = {x*2p + g^x mod p : x=0..p-1} — provably Sidon, structurally different from quadratic ET
# Then VLNS (Variable Large Neighborhood Search) with k=5 removal for deeper search

import time
import random


def primitive_root_mod_p(p):
    """Find smallest primitive root mod p."""
    phi = p - 1
    factors = set()
    n = phi
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    for g in range(2, p):
        if all(pow(g, phi // q, p) != 1 for q in factors):
            return g
    return 2


def ruzsa_primitive_root_scaled(p):
    """Ruzsa-Lindstrom: S = {x*2p + g^x mod p : x=0..p-1}.

    Key: the 2p spacing ensures high-part increments (2p) exceed max low-part
    variation (p-1), so no carry-induced collisions. Provably Sidon.
    Different from quadratic ET ({2ip + i^2 mod p}) — uses exponential not polynomial.
    """
    g = primitive_root_mod_p(p)
    S = []
    for x in range(p):
        val = x * 2 * p + pow(g, x, p)
        if val <= 10000:
            S.append(val)
    return sorted(S)


def greedy_extend(base_set, N=10000):
    """Greedily extend a Sidon set by scanning candidates in order."""
    S = sorted(base_set)
    used_diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            used_diffs.add(S[j] - S[i])

    S_set = set(S)
    for c in range(N + 1):
        if c in S_set:
            continue
        ok = True
        new_diffs = []
        for x in S:
            d = abs(c - x)
            if d in used_diffs:
                ok = False
                break
            if d in new_diffs:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            S.append(c)
            S.sort()
            used_diffs.update(new_diffs)
            S_set.add(c)

    return sorted(S)


def greedy_extend_from_candidates(current_set, candidates, N=10000):
    """Greedily extend from a given candidate list (already filtered)."""
    S = sorted(current_set)
    used_diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            used_diffs.add(S[j] - S[i])

    S_set = set(S)
    for c in candidates:
        if c in S_set or c < 0 or c > N:
            continue
        ok = True
        new_diffs = []
        for x in S:
            d = abs(c - x)
            if d in used_diffs:
                ok = False
                break
            if d in new_diffs:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            S.append(c)
            S.sort()
            used_diffs.update(new_diffs)
            S_set.add(c)

    return sorted(S)


def vlns(initial_set, N=10000, time_limit=90, k_min=3, k_max=10):
    """Variable Large Neighborhood Search.

    Repeatedly: remove k random elements, greedily repair, accept if improved.
    k varies from k_min to k_max to explore different neighborhood sizes.
    """
    best = sorted(initial_set)
    current = best[:]
    t0 = time.time()
    iterations = 0
    improvements = 0

    while time.time() - t0 < time_limit:
        k = random.randint(k_min, min(k_max, len(current) - 10))

        # Destroy: remove k random elements
        to_remove = set(random.sample(current, k))
        remaining = [x for x in current if x not in to_remove]

        # Repair: greedily add elements from {0..N} \ remaining
        # Use random order to explore different repairs
        all_cands = list(range(N + 1))
        random.shuffle(all_cands)
        repaired = greedy_extend_from_candidates(remaining, all_cands, N)

        iterations += 1

        if len(repaired) > len(best):
            best = repaired[:]
            current = repaired[:]
            improvements += 1
        elif len(repaired) >= len(current):
            current = repaired[:]
        elif random.random() < 0.05:
            # Small probability to accept worsening (escape local optima)
            current = repaired[:]

    elapsed = time.time() - t0
    print(f"  VLNS: {iterations} iterations, {improvements} improvements, "
          f"{elapsed:.1f}s, best={len(best)}")
    return best


def entrypoint():
    random.seed(42)

    # Ruzsa-Lindstrom primitive root p=71 (different from quadratic ET)
    p = 71
    base = ruzsa_primitive_root_scaled(p)
    print(f"Ruzsa-Lindstrom base (p={p}): {len(base)} elements, "
          f"range={min(base)}-{max(base)}")

    # Initial greedy extension
    extended = greedy_extend(base, N=10000)
    print(f"After greedy extension: {len(extended)} elements")

    # VLNS from this base
    result = vlns(extended, N=10000, time_limit=90, k_min=3, k_max=15)
    print(f"After VLNS: {len(result)} elements")

    return sorted(result)


if __name__ == "__main__":
    result = entrypoint()
    import sys
    sys.path.insert(0, 'problem')
    from helpers.core import is_sidon, count_violations
    print(f"Final: {len(result)} elements")
    print(f"Is Sidon: {is_sidon(result)}, violations: {count_violations(result)}")
    print(f"Range: {min(result)}-{max(result)}")
