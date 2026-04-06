# fitness: TBD
"""
Probabilistic alteration method for Sidon sets.

1. Sample random subset with prob p
2. Iteratively remove highest-violation element until set is valid Sidon
3. Greedy extend with shuffled candidates
4. Run many seeds, keep best
"""

import random
import bisect
import sys

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem')


def build_violations(S):
    """Returns (diff_pairs dict, per-element violation count list)."""
    diff_pairs = {}
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            d = S[j] - S[i]
            if d not in diff_pairs:
                diff_pairs[d] = []
            diff_pairs[d].append((i, j))
    viol = [0] * len(S)
    for d, pairs in diff_pairs.items():
        if len(pairs) > 1:
            seen = set()
            for (i, j) in pairs:
                seen.add(i); seen.add(j)
            for idx in seen:
                viol[idx] += 1
    return diff_pairs, viol


def alteration_sidon(seed, p=0.013, N=10000):
    rng = random.Random(seed)
    S = sorted(x for x in range(N + 1) if rng.random() < p)

    # Iteratively remove highest-violation element
    while True:
        _, viol = build_violations(S)
        max_v = max(viol) if viol else 0
        if max_v == 0:
            break
        worst = max(range(len(S)), key=lambda i: (viol[i], S[i]))
        S.pop(worst)

    # S is now a valid Sidon set. Build used_diffs for extension.
    used_diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            used_diffs.add(S[j] - S[i])

    S_set = set(S)
    remaining = [x for x in range(N + 1) if x not in S_set]
    rng.shuffle(remaining)

    for c in remaining:
        ok = True
        new_diffs = []
        for x in S:
            d = abs(c - x)
            if d in used_diffs or d in new_diffs:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            bisect.insort(S, c)
            for d in new_diffs:
                used_diffs.add(d)

    return S


def entrypoint():
    best = []
    # Grid of seeds × probabilities
    configs = [(p, seed) for p in [0.010, 0.012, 0.013, 0.015] for seed in range(40)]
    for p, seed in configs:
        S = alteration_sidon(seed, p=p)
        if len(S) > len(best):
            best = S
    return best


if __name__ == '__main__':
    import time
    t = time.time()
    # Quick test first
    S = alteration_sidon(0, p=0.013)
    print(f"Single seed test: size={len(S)}, time={time.time()-t:.2f}s")
    t2 = time.time()
    result = entrypoint()
    print(f"Full run: size={len(result)}, time={time.time()-t2:.1f}s")
