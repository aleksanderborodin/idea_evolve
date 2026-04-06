# fitness: 65
# approach: spread_first_greedy_plus_lns
# Two-phase search:
# Phase 1: "spread-first" greedy — always pick the valid candidate that
#   maximizes the minimum distance to existing elements (encourages
#   well-spread sets different from ascending-order greedy).
#   Use sampling for speed; run multiple restarts.
# Phase 2: LNS improvement on the best spread-first result.
#   Fast incremental difference tracking: O(k*|S|) per removal step
#   instead of O(|S|^2) rebuild.
#
# The spread-first heuristic naturally explores different structural
# territory than the standard greedy (which builds dense low-index sets)
# or the Singer set (which is algebraically defined).

import random
import time


def spread_first_greedy(N, sample_size, rng):
    """Greedy that always picks the valid candidate with max min-distance to S."""
    S = []
    used_diffs = set()
    # Seed: start from a random element
    first = rng.randint(0, N)
    S.append(first)
    candidates = list(range(N + 1))
    candidates.remove(first)

    while candidates:
        if len(candidates) <= sample_size:
            to_check = candidates
        else:
            to_check = rng.sample(candidates, sample_size)

        best_c = None
        best_score = -1
        best_diffs = None

        for c in to_check:
            new_diffs = []
            ok = True
            for x in S:
                d = abs(c - x)
                if d in used_diffs or d in new_diffs:
                    ok = False
                    break
                new_diffs.append(d)

            if ok:
                # Score: minimum distance to any existing element (spread-first)
                min_dist = min(abs(c - x) for x in S)
                if min_dist > best_score:
                    best_score = min_dist
                    best_c = c
                    best_diffs = new_diffs

        if best_c is None:
            # Scan all remaining candidates for a valid one
            found = False
            for c in candidates:
                if c in to_check:
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
                    used_diffs.update(new_diffs)
                    candidates.remove(c)
                    found = True
                    break
            if not found:
                break
        else:
            S.append(best_c)
            used_diffs.update(best_diffs)
            candidates.remove(best_c)

    return S, used_diffs


def lns_improve(S, used_diffs, N, time_budget, rng):
    """LNS hill-climbing with fast incremental diff tracking."""
    S = list(S)
    used_diffs = set(used_diffs)
    best = S[:]
    all_cands = list(range(N + 1))
    no_imp = 0

    deadline = time.time() + time_budget

    while time.time() < deadline:
        # Adaptive k
        if no_imp < 5:
            k = rng.randint(2, 8)
        elif no_imp < 20:
            k = rng.randint(8, 20)
        else:
            k = rng.randint(15, max(16, len(S) // 3))
            no_imp = 0

        k = min(k, max(1, len(S) - 3))

        # Copy state
        S_new = S[:]
        diffs_new = set(used_diffs)
        set_new = set(S_new)

        # Remove k elements with incremental diff update
        to_remove = rng.sample(S_new, k)
        for r in to_remove:
            S_new.remove(r)
            set_new.discard(r)
            for x in S_new:
                diffs_new.discard(abs(r - x))

        # Greedily extend with random ordering
        remaining = [c for c in all_cands if c not in set_new]
        rng.shuffle(remaining)

        for c in remaining:
            nd = []
            ok = True
            for x in S_new:
                d = abs(c - x)
                if d in diffs_new or d in nd:
                    ok = False
                    break
                nd.append(d)
            if ok:
                S_new.append(c)
                set_new.add(c)
                diffs_new.update(nd)

        if len(S_new) >= len(S):
            S = S_new
            used_diffs = diffs_new
            if len(S) > len(best):
                best = S[:]
                no_imp = 0
            else:
                no_imp += 1
        else:
            no_imp += 1

    return best


def entrypoint():
    N = 10000
    TIME_LIMIT = 24.0
    rng = random.Random()
    start = time.time()

    best = []
    best_diffs = set()

    # Phase 1: multiple spread-first greedy restarts (~8 seconds)
    phase1_deadline = start + 8.0
    sample_size = 150  # candidates to sample per greedy step

    while time.time() < phase1_deadline:
        S, ud = spread_first_greedy(N, sample_size, rng)
        if len(S) > len(best):
            best = S[:]
            best_diffs = ud.copy()

    # Phase 2: LNS improvement on best spread-first result
    remaining_time = TIME_LIMIT - (time.time() - start)
    if remaining_time > 1.0 and best:
        best = lns_improve(best, best_diffs, N, remaining_time, rng)

    return sorted(best)
