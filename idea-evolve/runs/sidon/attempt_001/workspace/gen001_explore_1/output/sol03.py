# fitness: TBD
"""
Push for 100 elements via aggressive perturbation of Singer set.

sol02 found 99 by removing 1-3 elements and adding back new ones.
This solution tries:
1. Larger perturbations (remove up to 5 elements)
2. Simulated annealing on top of Singer set
3. Multiple random seeds for the greedy restarts
"""
import time
import random


def _singer_set():
    p = 97
    B, C = 0, 2

    def mul(u, v):
        u0, u1, u2 = u
        v0, v1, v2 = v
        w = [0] * 5
        for i, ui in enumerate([u0, u1, u2]):
            for j, vj in enumerate([v0, v1, v2]):
                w[i + j] += ui * vj
        w[2] -= w[4] * B
        w[1] -= w[4] * C
        w[1] -= w[3] * B
        w[0] -= w[3] * C
        return (w[0] % p, w[1] % p, w[2] % p)

    v = p * p + p + 1
    gen = (5, 1, 0)
    D = []
    identity = (1, 0, 0)
    current = identity
    for k in range(v):
        if current[2] == 0 and current != (0, 0, 0):
            D.append(k)
        current = mul(current, gen)
    return D


def _greedy_sidon_from(seed_set, candidates):
    """Build Sidon set: start with seed_set (assumed valid), extend with candidates."""
    S = list(seed_set)
    used_diffs = set()
    S_sorted = sorted(S)
    for i in range(len(S_sorted)):
        for j in range(i + 1, len(S_sorted)):
            used_diffs.add(S_sorted[j] - S_sorted[i])

    for c in candidates:
        new_diffs = set()
        ok = True
        for x in S:
            d = abs(c - x)
            if d in used_diffs or d in new_diffs:
                ok = False
                break
            new_diffs.add(d)
        if ok:
            S.append(c)
            used_diffs.update(new_diffs)
    return S


def _greedy_sidon(candidates):
    """Build Sidon set greedily from scratch."""
    S = []
    used_diffs = set()
    for c in candidates:
        new_diffs = set()
        ok = True
        for x in S:
            d = abs(c - x)
            if d in used_diffs or d in new_diffs:
                ok = False
                break
            new_diffs.add(d)
        if ok:
            S.append(c)
            used_diffs.update(new_diffs)
    return S


def entrypoint():
    t0 = time.time()
    deadline = t0 + 115  # 115 second budget

    base = _singer_set()  # 98 elements
    best = list(base)
    base_set = set(base)

    all_cands = list(range(10001))
    non_singer = [c for c in all_cands if c not in base_set]

    def try_perturbation(k_remove, n_trials, rng):
        nonlocal best
        for _ in range(n_trials):
            if time.time() > deadline:
                return
            removed = rng.sample(base, k_remove)
            removed_set = set(removed)
            seed = sorted(base_set - removed_set)

            # Shuffle non-singer candidates and try extending
            cands = rng.sample(non_singer, len(non_singer))
            extended = _greedy_sidon_from(seed, cands)

            # Also try adding back removed elements
            missing = [x for x in removed if x not in extended]
            if missing:
                extended = _greedy_sidon_from(extended, missing)

            if len(extended) > len(best):
                best = sorted(extended)

    rng = random.Random(42)

    # Small perturbations first (fast, many trials)
    try_perturbation(1, 500, rng)
    try_perturbation(2, 500, rng)
    try_perturbation(3, 300, rng)
    try_perturbation(4, 200, rng)
    try_perturbation(5, 150, rng)

    # Larger perturbations
    for k in [6, 7, 8, 10, 12, 15]:
        try_perturbation(k, 100, rng)

    # Random restart greedy
    while time.time() < deadline:
        cands = rng.sample(all_cands, len(all_cands))
        S = _greedy_sidon(cands)
        if len(S) > len(best):
            best = sorted(S)

    return sorted(best)
