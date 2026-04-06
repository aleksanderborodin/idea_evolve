# fitness: TBD
"""
sol02: Min-blocking greedy Sidon set construction.

Algorithm: at each step, pick the valid candidate c that would block
the fewest OTHER valid candidates if added.

Blocking from adding c: for each new difference d = |c - existing_elem|,
elements c+d and c-d become blocked. Sum these over all new differences.

Multiple random tie-breaking seeds to escape local minima.
"""

import random


def _min_blocking_greedy(N=10000, seed=42):
    rng = random.Random(seed)
    S = []
    used_diffs = set()
    conflict = [0] * (N + 1)  # conflict[c] = # used_diffs that would block c

    # All elements start valid
    # valid = set(range(N + 1))  -- tracked via conflict array

    while True:
        # Gather valid candidates (conflict == 0)
        # For large N this scan is O(N) per step; optimize with a sorted structure if needed
        candidates = [c for c in range(N + 1) if conflict[c] == 0]
        if not candidates:
            break

        # Compute blocking score for each candidate
        # blocking(c) = # of valid candidates c' that would become newly conflicted
        #   after adding c (via new differences |c - s| for s in S)
        best_score = float('inf')
        best_ties = []

        for c in candidates:
            # New differences if we add c
            new_diffs = []
            for s in S:
                d = abs(c - s)
                new_diffs.append(d)

            # Count newly blocked candidates
            score = 0
            seen_blocked = set()
            for d in new_diffs:
                cp = c + d
                if 0 <= cp <= N and conflict[cp] == 0 and cp not in seen_blocked and cp != c:
                    score += 1
                    seen_blocked.add(cp)
                cm = c - d
                if 0 <= cm <= N and conflict[cm] == 0 and cm not in seen_blocked and cm != c:
                    score += 1
                    seen_blocked.add(cm)

            if score < best_score:
                best_score = score
                best_ties = [c]
            elif score == best_score:
                best_ties.append(c)

        # Random tie-break
        c = rng.choice(best_ties)

        # Add c to S
        new_diffs_c = [abs(c - s) for s in S]
        S.append(c)
        used_diffs.update(new_diffs_c)

        # Update conflict counts
        for d in new_diffs_c:
            cp = c + d
            if 0 <= cp <= N:
                conflict[cp] += 1
            cm = c - d
            if 0 <= cm <= N and cm != c:
                conflict[cm] += 1
        # c itself is now in S, mark it unavailable
        conflict[c] += 10000  # effectively blocked

    return sorted(S)


def entrypoint():
    N = 10000
    best = []
    # Try a few different seeds
    for seed in [42, 0, 1, 7, 13, 99, 137, 256, 512, 1000]:
        result = _min_blocking_greedy(N, seed)
        if len(result) > len(best):
            best = result
    return best


if __name__ == '__main__':
    import sys
    result = entrypoint()
    print(f"Size: {len(result)}")
    diffs = set()
    valid = True
    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            d = result[j] - result[i]
            if d in diffs:
                valid = False
                break
            diffs.add(d)
        if not valid:
            break
    print(f"Valid Sidon: {valid}")
