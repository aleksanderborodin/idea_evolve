# fitness: 65
# approach: Multi-seed random greedy + aggressive VLNS (k=10-40)
# Key insight: algebraic constructions all top out at ~75 with local search.
# Start from random-order greedy sets (~66) and use large-neighborhood search
# to explore non-algebraic basins. Multiple random seeds.

import time
import random


def random_greedy_sidon(seed, N=10000):
    """Build greedy Sidon set from random candidate ordering."""
    rng = random.Random(seed)
    candidates = list(range(N + 1))
    rng.shuffle(candidates)

    S = []
    used_diffs = set()
    for c in candidates:
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
            used_diffs.update(new_diffs)

    return sorted(S)


def fast_repair(remaining, N=10000, seed=None):
    """Greedily repair a partial set using random candidate order."""
    rng = random.Random(seed)
    S = sorted(remaining)

    used_diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            used_diffs.add(S[j] - S[i])

    # Try candidates in random order to explore different repairs
    candidates = list(range(N + 1))
    rng.shuffle(candidates)

    S_set = set(S)
    for c in candidates:
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


def vlns_aggressive(initial_set, N=10000, time_limit=110, k_min=10, k_max=40):
    """Aggressive VLNS with large removal neighborhoods.

    Large k means we explore very different configurations per iteration.
    Accepts any non-worsening moves, and occasionally accepts worsening moves.
    """
    best = sorted(initial_set)
    current = best[:]
    t0 = time.time()
    iteration = 0
    improvements = 0
    stagnation = 0
    seed = 0

    while time.time() - t0 < time_limit:
        k = random.randint(k_min, min(k_max, len(current) - 5))

        # Destroy: remove k random elements
        to_remove = set(random.sample(current, k))
        remaining = [x for x in current if x not in to_remove]

        # Repair: random-order greedy
        repaired = fast_repair(remaining, N, seed=seed)
        seed += 1
        iteration += 1

        if len(repaired) > len(best):
            best = sorted(repaired)
            current = best[:]
            improvements += 1
            stagnation = 0
        elif len(repaired) >= len(current):
            current = sorted(repaired)
            stagnation = 0
        else:
            stagnation += 1
            # After 200 stagnation steps, restart from best
            if stagnation > 200:
                current = best[:]
                stagnation = 0

    elapsed = time.time() - t0
    print(f"  VLNS: {iteration} iters, {improvements} improvements, "
          f"elapsed={elapsed:.1f}s, best={len(best)}")
    return best


def entrypoint():
    random.seed(0)

    # Try multiple random-greedy starting points
    print("Building random-greedy starting sets...")
    best_start = None
    best_size = 0
    for seed in range(20):
        S = random_greedy_sidon(seed, N=10000)
        if len(S) > best_size:
            best_size = len(S)
            best_start = S

    print(f"Best random-greedy start: {best_size} elements")

    # Aggressive VLNS from best random start
    result = vlns_aggressive(best_start, N=10000, time_limit=110, k_min=10, k_max=40)
    print(f"After aggressive VLNS: {len(result)} elements")

    return sorted(result)


if __name__ == "__main__":
    result = entrypoint()
    import sys
    sys.path.insert(0, 'problem')
    from helpers.core import is_sidon, count_violations
    print(f"Final: {len(result)} elements")
    print(f"Is Sidon: {is_sidon(result)}, violations: {count_violations(result)}")
    print(f"Range: {min(result)}-{max(result)}")
