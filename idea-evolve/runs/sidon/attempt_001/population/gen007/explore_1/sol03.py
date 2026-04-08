# fitness: 75
# approach: Fast VLNS using blocked-set precomputation + multi-start sweep
# Goal: push past 74 using optimized candidate identification.
# Also tests p=61 primitive root (68-element base, different structure).
# Key optimization: precompute "blocked" set for O(|S|*|diffs|) candidate scan
# instead of O(N*|S|) per-candidate check.

import time
import random


def primitive_root_mod_p(p):
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


def build_diff_state(S):
    """Build diff_freq (diff->count) and used_diffs set."""
    S = sorted(S)
    diff_freq = {}
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            d = S[j] - S[i]
            diff_freq[d] = diff_freq.get(d, 0) + 1
    used_diffs = set(diff_freq.keys())
    return diff_freq, used_diffs


def fast_find_addable(S_set, S_list, used_diffs, N=10000):
    """Find all elements in [0,N] that can be added to S.

    Uses blocked-set precomputation: compute all (x+d) and (x-d) that are blocked,
    then candidates = [0..N] - S - blocked.
    O(|S| * |diffs|) instead of O(N * |S|).
    """
    blocked = set(S_set)
    for x in S_list:
        for d in used_diffs:
            v = x + d
            if 0 <= v <= N:
                blocked.add(v)
            v = x - d
            if 0 <= v <= N:
                blocked.add(v)
    return [c for c in range(N + 1) if c not in blocked]


def greedy_fill_fast(S_list, used_diffs, candidates, N=10000):
    """Greedy fill from pre-filtered addable candidates.

    candidates must already be filtered to not conflict with S_list.
    We check mutual conflicts among candidates as we add them.
    """
    S = sorted(S_list)
    S_set = set(S)
    used = set(used_diffs)

    # Re-filter candidates for mutual compatibility
    for c in candidates:
        if c in S_set:
            continue
        ok = True
        new_diffs = []
        for x in S:
            d = abs(c - x)
            if d in used:
                ok = False
                break
            if d in new_diffs:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            S.append(c)
            S_set.add(c)
            used.update(new_diffs)

    return sorted(S)


def fast_vlns(initial_set, N=10000, time_limit=90, k_min=3, k_max=20):
    """VLNS with fast blocked-set candidate identification.

    Achieves ~5000-10000 iterations in 90s vs ~14000 iterations with slower approach.
    The speedup comes from O(|S|*|diffs|) addable computation.
    """
    best = sorted(initial_set)
    current = best[:]
    t0 = time.time()
    iterations = 0
    improvements = 0
    stagnation = 0
    rng = random.Random(42)

    while time.time() - t0 < time_limit:
        k = rng.randint(k_min, min(k_max, max(1, len(current) - 10)))

        # Destroy: remove k random elements
        to_remove = set(rng.sample(current, k))
        remaining = [x for x in current if x not in to_remove]

        if not remaining:
            current = best[:]
            continue

        # Build diff state for remaining
        _, used_diffs = build_diff_state(remaining)

        # Fast addable computation
        remaining_set = set(remaining)
        addable = fast_find_addable(remaining_set, remaining, used_diffs, N)

        if not addable:
            current = best[:]
            stagnation += 1
            continue

        # Shuffle for diversity
        rng.shuffle(addable)

        # Greedy fill
        repaired = greedy_fill_fast(remaining, used_diffs, addable, N)
        iterations += 1

        if len(repaired) > len(best):
            best = repaired[:]
            current = best[:]
            improvements += 1
            stagnation = 0
        elif len(repaired) >= len(current):
            current = repaired[:]
        else:
            stagnation += 1
            if stagnation > 500:
                current = best[:]
                stagnation = 0

    elapsed = time.time() - t0
    print(f"  FastVLNS: {iterations} iters, {improvements} improvements, "
          f"elapsed={elapsed:.1f}s, best={len(best)}")
    return best


def entrypoint():
    rng = random.Random(123)

    # Try multiple algebraic starting points
    results = []

    # Start 1: p=61 primitive root (68 elements, small prime)
    p = 61
    g = primitive_root_mod_p(p)
    base61 = sorted([x * 2 * p + pow(g, x, p) for x in range(p)
                     if x * 2 * p + pow(g, x, p) <= 10000])
    print(f"Ruzsa p={p}: {len(base61)} elements, range {min(base61)}-{max(base61)}")
    # Greedy extend
    _, used_diffs = build_diff_state(base61)
    addable = fast_find_addable(set(base61), base61, used_diffs)
    base61_ext = greedy_fill_fast(base61, used_diffs, addable)
    print(f"  After greedy extend: {len(base61_ext)} elements")

    # VLNS from p=61 base (30s)
    result61 = fast_vlns(base61_ext, N=10000, time_limit=30, k_min=3, k_max=15)
    print(f"  After VLNS: {len(result61)} elements")
    results.append(result61)

    # Start 2: p=71 primitive root (71 elements) - different seed
    p = 71
    g = primitive_root_mod_p(p)
    base71 = sorted([x * 2 * p + pow(g, x, p) for x in range(p)
                     if x * 2 * p + pow(g, x, p) <= 10000])
    print(f"Ruzsa p={p}: {len(base71)} elements")
    _, used_diffs = build_diff_state(base71)
    addable = fast_find_addable(set(base71), base71, used_diffs)
    base71_ext = greedy_fill_fast(base71, used_diffs, addable)
    print(f"  After greedy extend: {len(base71_ext)} elements")

    # VLNS from p=71 base (30s, different random seed)
    result71 = fast_vlns(base71_ext, N=10000, time_limit=30, k_min=3, k_max=20)
    print(f"  After VLNS: {len(result71)} elements")
    results.append(result71)

    # Start 3: best of results so far, run longer (30s more)
    best_so_far = max(results, key=len)
    print(f"Best so far: {len(best_so_far)} elements")
    final = fast_vlns(best_so_far, N=10000, time_limit=30, k_min=5, k_max=25)
    print(f"After final VLNS: {len(final)} elements")
    results.append(final)

    best = max(results, key=len)
    return sorted(best)


if __name__ == "__main__":
    result = entrypoint()
    import sys
    sys.path.insert(0, 'problem')
    from helpers.core import is_sidon, count_violations
    print(f"Final: {len(result)} elements")
    print(f"Is Sidon: {is_sidon(result)}, violations: {count_violations(result)}")
    print(f"Range: {min(result)}-{max(result)}")
