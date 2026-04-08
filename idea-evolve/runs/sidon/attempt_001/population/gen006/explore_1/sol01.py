# fitness: 66
"""
DFS/Backtracking approach for Sidon sets — testing idea_005.

First empirical test of systematic backtracking with constraint propagation.
Goal: determine whether DFS can exceed the greedy ceiling of 70 for N=10000.

Algorithm:
1. DFS building a Sidon set element-by-element from a candidate list
2. Pruning: position-count upper bound at each DFS node
3. Randomized restarts: multiple runs with shuffled candidate order
4. Time limit: 27s, returns best found

Key insight: Unlike greedy (one pass), DFS can backtrack and try different
choices when the current path dead-ends. Whether this helps in 27s is the
experiment we're running.
"""
import time
import random


def entrypoint():
    N = 10000
    TIME_LIMIT = 27.0
    start_t = time.time()
    state = {'best': []}  # mutable container to avoid nonlocal issues

    def dfs_run(candidates, target):
        """
        DFS over a fixed candidate ordering.
        Updates state['best'] with the largest valid Sidon set found.
        """
        S = []
        D = set()

        def recurse(idx):
            if time.time() - start_t > TIME_LIMIT:
                return True  # timeout

            n = len(S)
            if n > len(state['best']):
                state['best'] = S[:]

            if n == target:
                return True

            # Upper bound: even if we add ALL remaining candidates we can't reach target
            if n + (len(candidates) - idx) < target:
                return False

            for i in range(idx, len(candidates)):
                # Tighter bound as we advance
                if n + (len(candidates) - i) < target:
                    break

                if time.time() - start_t > TIME_LIMIT:
                    return True

                c = candidates[i]

                # Check if c can be added to current set S
                new_diffs = set()
                ok = True
                for x in S:
                    d = abs(c - x)
                    if d in D or d in new_diffs:
                        ok = False
                        break
                    new_diffs.add(d)

                if not ok:
                    continue

                # Add c (in-place mutation for performance)
                S.append(c)
                D.update(new_diffs)

                if recurse(i + 1):
                    return True

                # Backtrack (new_diffs was disjoint from D, so this is safe)
                S.pop()
                D.difference_update(new_diffs)

            return False

        recurse(0)

    # --- Phase 1: Calibrate on N=200 ---
    cal_start = time.time()
    cal_cands = list(range(201))
    dfs_run(cal_cands, 16)  # sqrt(200) ≈ 14.1, target 16
    cal_time = time.time() - cal_start
    cal_size = len(state['best'])
    state['best'] = []  # reset for main run

    # --- Phase 2: Sequential DFS on N=10000 ---
    # Forward pass finds greedy solution quickly, backtracking explores alternatives
    seq_cands = list(range(N + 1))
    dfs_run(seq_cands, 75)

    # --- Phase 3: Randomized restarts ---
    # Different orderings explore different parts of the search tree
    attempt = 0
    while time.time() - start_t < TIME_LIMIT - 0.5:
        random.seed(attempt)
        shuffled = list(range(N + 1))
        random.shuffle(shuffled)
        target = max(len(state['best']) + 1, 70)
        dfs_run(shuffled, target)
        attempt += 1

    result = state['best']

    # Fallback: if DFS found nothing useful, use greedy
    if len(result) < 50:
        from helpers.search import greedy_sidon
        result = greedy_sidon(range(N + 1))

    return sorted(result)
