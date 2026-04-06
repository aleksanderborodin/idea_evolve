# fitness: 0 (violations bug)
# approach: large_neighborhood_search
# Large Neighborhood Search (LNS) on Sidon sets.
# 1. Start from deterministic greedy (66 elements).
# 2. Each LNS step: remove k random elements, shuffle remaining candidates,
#    greedily rebuild the set.
# 3. Accept new set if size >= current (hill climbing).
# 4. Track global best.
# 5. If stuck for many steps, do a large restart with k=40 to escape.
#
# Key motivation: the Singer 102-element set has 40+ blockers per candidate.
# A set found by LNS may have different structural properties and fewer
# blockers, potentially extensible beyond 102.

import random
import time


def _build_used_diffs(S):
    """Build the set of all positive differences from a Sidon set."""
    diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            diffs.add(S[j] - S[i])
    return diffs


def _remove_elements(S, used_diffs, to_remove_set):
    """Remove elements in to_remove_set from S and update used_diffs in place.
    Returns the new S (list).  S must be sorted."""
    # First remove the diffs contributed by each element being removed
    new_S = [x for x in S if x not in to_remove_set]
    # Rebuild diffs from scratch on the smaller set (faster than tracking what to remove
    # when removing multiple elements at once)
    new_diffs = _build_used_diffs(new_S)
    return new_S, new_diffs


def _greedy_extend(S, used_diffs, candidates):
    """Greedily add candidates (in given order) to S.
    Modifies S and used_diffs in place."""
    in_S = set(S)
    for c in candidates:
        if c in in_S:
            continue
        new_diffs = []
        ok = True
        for x in S:
            d = abs(c - x)
            if d in used_diffs or d in new_diffs:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            S.append(c)
            in_S.add(c)
            used_diffs.update(new_diffs)
    return S, used_diffs


def entrypoint():
    N = 10000
    TIME_LIMIT = 24.0
    start = time.time()

    # Phase 1: deterministic greedy as starting point
    S = []
    used_diffs = set()
    for c in range(N + 1):
        new_diffs = []
        ok = True
        for x in S:
            d = abs(c - x)
            if d in used_diffs or d in new_diffs:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            S.append(c)
            used_diffs.update(new_diffs)

    best = S[:]
    best_diffs = used_diffs.copy()

    # Phase 2: LNS iterations
    no_improvement_streak = 0
    step = 0
    all_candidates = list(range(N + 1))

    while time.time() - start < TIME_LIMIT:
        step += 1

        # Adaptive k: remove more elements when stuck
        if no_improvement_streak < 10:
            k = random.randint(5, 20)
        elif no_improvement_streak < 30:
            k = random.randint(20, 40)
        else:
            # Big restart: remove most of the set, rebuild fresh
            k = max(5, len(S) - 20)
            no_improvement_streak = 0

        k = min(k, max(1, len(S) - 5))
        to_remove = set(random.sample(S, k))

        # Remove and rebuild
        new_S, new_diffs = _remove_elements(S, used_diffs, to_remove)

        # Shuffle remaining candidates and greedily extend
        remaining = [c for c in all_candidates if c not in set(new_S)]
        random.shuffle(remaining)
        new_S, new_diffs = _greedy_extend(new_S, new_diffs, remaining)

        if len(new_S) >= len(S):
            S = new_S
            used_diffs = new_diffs
            if len(S) > len(best):
                best = S[:]
                best_diffs = used_diffs.copy()
                no_improvement_streak = 0
            else:
                no_improvement_streak += 1
        else:
            no_improvement_streak += 1

    return sorted(best)
