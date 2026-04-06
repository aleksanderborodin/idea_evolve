# fitness: TBD
"""Iterated Local Search for Sidon sets.

Key idea: instead of maintaining a valid Sidon set at all times,
use a "relaxed" approach where we work on sets with some violations,
then repair. The target is |S| - penalty * violations.

Also implements: targeted swap where we identify which elements in S
are blocking the most near-addable candidates and prioritize swapping them.
"""

import random
import math
import time
import bisect


def entrypoint():
    N = 10000
    TIME_LIMIT = 27

    start_time = time.time()

    def build_diff_count(S_sorted):
        dc = {}
        for i in range(len(S_sorted)):
            for j in range(i + 1, len(S_sorted)):
                d = S_sorted[j] - S_sorted[i]
                dc[d] = dc.get(d, 0) + 1
        return dc

    def can_add(S_sorted, dc, x):
        for s in S_sorted:
            d = abs(x - s)
            if d in dc:
                return False
        return True

    def greedy_fill_sorted(S_sorted, dc, order=None):
        """Fill greedily in given order (default: 0..N sequential)."""
        S_set = set(S_sorted)
        if order is None:
            order = range(N + 1)
        for c in order:
            if c in S_set:
                continue
            new_diffs = []
            conflict = False
            for s in S_sorted:
                d = abs(c - s)
                if d in dc:
                    conflict = True
                    break
                new_diffs.append(d)
            if not conflict:
                bisect.insort(S_sorted, c)
                S_set.add(c)
                for d in new_diffs:
                    dc[d] = dc.get(d, 0) + 1
        return S_sorted, dc

    def clone_state(S_sorted, dc):
        return list(S_sorted), dict(dc)

    def remove_elem(S_sorted, dc, x):
        idx = bisect.bisect_left(S_sorted, x)
        S_sorted.pop(idx)
        for s in S_sorted:
            d = abs(x - s)
            dc[d] -= 1
            if dc[d] == 0:
                del dc[d]

    # --- Phase 1: Multi-start greedy ---
    best_S = []
    best_score = 0

    # Run #1: sequential greedy
    S = []
    dc = {}
    S, dc = greedy_fill_sorted(S, dc)
    if len(S) > best_score:
        best_S = list(S)
        best_score = len(S)

    # Run a few more with random-shuffled orders
    for _ in range(5):
        if time.time() - start_time > 3:
            break
        order = list(range(N + 1))
        random.shuffle(order)
        S = []
        dc = {}
        S, dc = greedy_fill_sorted(S, dc, order)
        if len(S) > best_score:
            best_S = list(S)
            best_score = len(S)

    # --- Phase 2: Iterated local search ---
    # Work from best_S. Strategy:
    # 1. Compute "blocking score" for each element in S:
    #    how many {0..N}\S elements does it block?
    # 2. Remove high-blockers, greedily fill, check if improved.

    def compute_conflict_counts(S_sorted, dc):
        """For each z in {0..N}\S, count how many of its diffs with S are in dc."""
        S_set = set(S_sorted)
        # For efficiency: build conflict_count array
        conflict_count = [0] * (N + 1)
        for s in S_sorted:
            for d in list(dc.keys()):
                # The pairs that create diff d: for z, if |z - s| = d and d in dc,
                # that means z is conflicted (there's another pair with diff d)
                # But we need |z - s| = d where d is already used
                # z = s + d or z = s - d
                for z in [s + d, s - d]:
                    if 0 <= z <= N and z not in S_set:
                        conflict_count[z] += 1
        return conflict_count

    def compute_blocking_score(S_sorted, dc):
        """For each s in S, how many non-S elements does removing s help?"""
        # After removing s, diff_count changes: all diffs |s - t| for t in S are removed
        # Then elements z that were blocked ONLY because diff |z - s| was in dc (placed by pair (s, t))
        # become unblocked
        # Quick approximation: count non-S elements z where |z - s| is in dc
        S_set = set(S_sorted)
        blocking = {}
        for s in S_sorted:
            count = 0
            for t in S_sorted:
                if t == s:
                    continue
                d = abs(s - t)  # this diff will be freed by removing s
                # Count how many z would benefit from d being freed
                for z in [s + d, s - d, t + d, t - d]:
                    if 0 <= z <= N and z not in S_set:
                        count += 1
            blocking[s] = count
        return blocking

    S_sorted = sorted(best_S)
    dc = build_diff_count(S_sorted)

    iteration = 0
    no_improve_count = 0

    while time.time() - start_time < TIME_LIMIT:
        iteration += 1

        move = random.random()

        if move < 0.5 or len(S_sorted) < 3:
            # Random perturbation: remove k elements, greedy fill in random order
            k = random.randint(3, min(20, len(S_sorted) // 3 + 2))
            saved_S, saved_dc = clone_state(S_sorted, dc)

            to_remove = random.sample(S_sorted, k)
            for x in to_remove:
                remove_elem(S_sorted, dc, x)

            order = list(range(N + 1))
            random.shuffle(order)
            S_sorted, dc = greedy_fill_sorted(S_sorted, dc, order)

            if len(S_sorted) > best_score:
                best_S = list(S_sorted)
                best_score = len(S_sorted)
                no_improve_count = 0
            elif len(S_sorted) < len(saved_S):
                # Reject: restore
                S_sorted, dc = saved_S, saved_dc
                no_improve_count += 1
            else:
                no_improve_count += 1

        else:
            # Targeted swap: remove highest-blocking element, try to add 2+
            # Quick version: remove a random element weighted towards "high blocker"
            blocking = compute_blocking_score(S_sorted, dc)
            total = sum(blocking.values()) + 1
            r = random.uniform(0, total)
            cumsum = 0
            removed = S_sorted[0]
            for s, b in blocking.items():
                cumsum += b
                if cumsum >= r:
                    removed = s
                    break

            saved_S, saved_dc = clone_state(S_sorted, dc)
            remove_elem(S_sorted, dc, removed)

            # Try to add 2 random candidates
            added = 0
            candidates = list(range(N + 1))
            random.shuffle(candidates)
            S_set = set(S_sorted)
            for c in candidates[:500]:  # sample 500 candidates
                if c not in S_set and can_add(S_sorted, dc, c):
                    new_diffs = []
                    for s in S_sorted:
                        new_diffs.append(abs(c - s))
                    bisect.insort(S_sorted, c)
                    S_set.add(c)
                    for d in new_diffs:
                        dc[d] = dc.get(d, 0) + 1
                    added += 1
                    if added >= 2:
                        break

            if len(S_sorted) > best_score:
                best_S = list(S_sorted)
                best_score = len(S_sorted)
                no_improve_count = 0
            elif len(S_sorted) < len(saved_S):
                S_sorted, dc = saved_S, saved_dc
                no_improve_count += 1
            else:
                no_improve_count += 1

        # Restart from best if stuck
        if no_improve_count > 200:
            S_sorted = sorted(best_S)
            dc = build_diff_count(S_sorted)
            no_improve_count = 0

    return best_S
