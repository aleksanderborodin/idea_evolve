# fitness: TBD
"""
Min-blocking greedy for Sidon sets — corrected implementation.

idea_016 had a critical bug: never blocked midpoints of pairs.
When adding element e to S, candidate x = (e+s)/2 for any s in S becomes
invalid because |x-e| = |x-s| (equal differences to two elements).
Standard ascending greedy achieves 66; this attempts to do better.

At each step: choose the valid candidate that blocks the fewest remaining candidates.
"""

import time


def min_blocking_greedy(N=10000, time_limit=110):
    """
    Min-blocking greedy Sidon set construction.
    valid[i] = True iff i is still a valid candidate.
    """
    valid = bytearray(N + 1)
    for i in range(N + 1):
        valid[i] = 1

    S = []
    used_diffs = set()
    start = time.time()

    while True:
        if time.time() - start > time_limit:
            break

        # Find best candidate: minimum blocking count
        best_c = -1
        min_blocks = N + 1

        # Scan all valid candidates
        for c in range(N + 1):
            if not valid[c]:
                continue

            # Compute blocking count for adding c:
            # 1. Candidates at c ± d for existing d in used_diffs (conflict with existing pairs)
            # 2. Candidates that are mirrors: 2c - s for s in S (equal diff to c and s)
            # 3. Midpoints (c + s)/2 for s in S with same parity (equal diffs)
            blocked = 0

            # Term 1: existing diffs conflict with c
            for d in used_diffs:
                x = c + d
                if x <= N and valid[x]:
                    blocked += 1
                x = c - d
                if x >= 0 and valid[x]:
                    blocked += 1

            # Term 2: new diffs from c block existing elements' neighbors
            new_diffs_c = []
            for s in S:
                nd = c - s if c > s else s - c  # abs(c-s)
                new_diffs_c.append(nd)
                # Candidates x at s ± nd (x's diff to s = nd, same as c's diff to s)
                x = s + nd  # = c (already going in S, not counted)
                # x = s - nd = 2s - c
                x = s + s - c
                if 0 <= x <= N and valid[x]:
                    blocked += 1
                # Also: x at c ± nd (x's diff to c = nd = c's diff to s → mirrors c through s)
                # x = c + nd = 2c - s
                x = c + c - s
                if 0 <= x <= N and valid[x] and x != c:
                    blocked += 1
                # x = c - nd = s (already in S, not valid)

            # Term 3: midpoints of (c, s): x = (c+s)//2 when same parity
            for s in S:
                if (c + s) % 2 == 0:
                    x = (c + s) // 2
                    if 0 <= x <= N and valid[x] and x != c:
                        blocked += 1

            if blocked < min_blocks:
                min_blocks = blocked
                best_c = c
                if blocked == 0:
                    break  # Can't do better

        if best_c < 0:
            break

        # Add best_c to S
        new_diffs = []
        for s in S:
            new_diffs.append(abs(best_c - s))

        S.append(best_c)
        valid[best_c] = 0

        # Update valid: mark all newly blocked candidates
        # 1. Candidates at best_c ± d for d in used_diffs
        for d in used_diffs:
            x = best_c + d
            if x <= N:
                valid[x] = 0
            x = best_c - d
            if x >= 0:
                valid[x] = 0

        # 2. New diffs × all elements in S (including best_c)
        for nd in new_diffs:
            for e in S:  # includes best_c (just appended)
                x = e + nd
                if x <= N:
                    valid[x] = 0
                x = e - nd
                if x >= 0:
                    valid[x] = 0

        # 3. Midpoints of (best_c, s) for each s in S_prev = S[:-1]
        for s in S[:-1]:  # S_prev
            if (best_c + s) % 2 == 0:
                x = (best_c + s) // 2
                if 0 <= x <= N:
                    valid[x] = 0

        used_diffs.update(new_diffs)

    return sorted(S)


def entrypoint():
    return min_blocking_greedy(N=10000, time_limit=110)
