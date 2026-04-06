# fitness: 67
# approach: lns_fixed
# Large Neighborhood Search (LNS) with correct difference tracking.
# Bug fix over sol02: _build_used_diffs now uses abs() so unsorted sets work.
# Strategy: start from deterministic greedy (66), then repeatedly remove k
# random elements and greedily rebuild.  Hill-climbing acceptance.
# When stuck: increase k to force diversity.

import random
import time


def _build_used_diffs(S):
    """Build set of all positive pairwise differences. Works for any ordering."""
    diffs = set()
    n = len(S)
    for i in range(n):
        for j in range(i + 1, n):
            diffs.add(abs(S[j] - S[i]))
    return diffs


def _greedy_extend(S, used_diffs, candidates_iter):
    """Greedily add candidates to S in the given order.
    S must be a list; used_diffs must be a set of positive differences for S.
    Modifies S and used_diffs in place."""
    in_S = set(S)
    for c in candidates_iter:
        if c in in_S:
            continue
        new_diffs = []
        ok = True
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
            in_S.add(c)
            used_diffs.update(new_diffs)
    return S, used_diffs


def entrypoint():
    N = 10000
    TIME_LIMIT = 24.0
    start = time.time()

    # Build starting solution: deterministic greedy
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
    all_candidates = list(range(N + 1))

    no_imp = 0
    step = 0

    while time.time() - start < TIME_LIMIT:
        step += 1

        # Adaptive k: small when making progress, large when stuck
        if no_imp < 5:
            k = random.randint(3, 15)
        elif no_imp < 20:
            k = random.randint(15, 35)
        else:
            k = random.randint(30, max(31, len(S) - 10))
            no_imp = 0

        k = min(k, max(1, len(S) - 3))

        # Remove k random elements from S
        to_remove = set(random.sample(S, k))
        new_S = [x for x in S if x not in to_remove]
        new_diffs = _build_used_diffs(new_S)

        # Shuffle remaining candidates and greedily add
        remaining = [c for c in all_candidates if c not in set(new_S)]
        random.shuffle(remaining)
        _greedy_extend(new_S, new_diffs, remaining)

        if len(new_S) >= len(S):
            S = new_S
            used_diffs = new_diffs
            if len(S) > len(best):
                best = S[:]
                no_imp = 0
            else:
                no_imp += 1
        else:
            no_imp += 1

    return sorted(best)
