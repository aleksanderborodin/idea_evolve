# fitness: 63
# approach: randomized_greedy_restarts
# Randomized greedy with many random-shuffle restarts.
# At each restart we shuffle {0,...,10000} randomly and greedily add
# elements in that order.  We keep the best result across all restarts.
# This is the simplest non-algebraic baseline.

import random
import time


def entrypoint():
    N = 10000
    TIME_LIMIT = 25.0  # seconds
    start = time.time()

    best = []
    restart = 0

    while time.time() - start < TIME_LIMIT:
        restart += 1
        candidates = list(range(N + 1))
        random.shuffle(candidates)

        S = []
        used_diffs = set()

        for c in candidates:
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

        if len(S) > len(best):
            best = S[:]

    return sorted(best)
