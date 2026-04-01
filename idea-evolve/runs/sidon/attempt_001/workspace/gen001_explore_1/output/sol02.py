# fitness: TBD
"""
Attempt to exceed 98 elements via Singer set + perturbation search.

The Singer set for q=97 is perfect (all differences 1..9506 covered), so no element
can be added directly. Strategy: remove a few elements to "free up" differences,
then greedily add back new elements including candidates beyond 9506.

Uses multi-restart local search with time limit.
"""
import time
import random


def _singer_set():
    """Return the 98-element Singer difference set in [0, 9506]."""
    p = 97
    B, C = 0, 2  # Irreducible cubic x^3 + 2 over GF(97)

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

    v = p * p + p + 1  # 9507
    gen = (5, 1, 0)
    D = []
    identity = (1, 0, 0)
    current = identity
    for k in range(v):
        if current[2] == 0 and current != (0, 0, 0):
            D.append(k)
        current = mul(current, gen)
    return D


def _build_diffs(S):
    """Build set of all positive differences in sorted S."""
    S = sorted(S)
    diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            diffs.add(S[j] - S[i])
    return diffs


def _greedy_extend(S, candidates, used_diffs):
    """Try to add elements from candidates without conflict."""
    S = sorted(S)
    ud = set(used_diffs)
    result = list(S)
    for c in candidates:
        new_diffs = set()
        ok = True
        for x in result:
            d = abs(c - x)
            if d in ud or d in new_diffs:
                ok = False
                break
            new_diffs.add(d)
        if ok:
            result.append(c)
            ud.update(new_diffs)
    return sorted(result)


def _greedy_sidon(candidates):
    """Build Sidon set greedily from candidates list."""
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
    random.seed(42)
    t0 = time.time()
    deadline = t0 + 55  # 55 second budget

    base = _singer_set()  # 98 elements in [0, 9506]
    best = list(base)

    # Full candidate pool: [0, 10000]
    all_candidates = list(range(10001))

    # Strategy 1: Remove k elements from Singer set, then try to add back more
    base_set = set(base)
    base_diffs = _build_diffs(base)

    for k_remove in [1, 2, 3]:
        if time.time() > deadline:
            break

        # Try removing each combination of k elements
        # For k=1: try all 98 choices
        # For k=2: sample random pairs
        # For k=3: sample random triples
        if k_remove == 1:
            remove_choices = [[x] for x in base]
        elif k_remove == 2:
            remove_choices = [
                random.sample(base, 2) for _ in range(200)
            ]
        else:
            remove_choices = [
                random.sample(base, 3) for _ in range(300)
            ]

        for removed in remove_choices:
            if time.time() > deadline:
                break

            # Build reduced set and its diffs
            reduced = sorted(set(base) - set(removed))
            ud = _build_diffs(reduced)

            # Candidates not in Singer set
            non_singer = [c for c in all_candidates if c not in base_set]

            # Greedy extend with non-singer candidates first
            extended = _greedy_extend(reduced, non_singer, ud)

            # Also try adding back the removed elements
            ud2 = _build_diffs(extended)
            extended2 = _greedy_extend(extended, removed, ud2)

            if len(extended2) > len(best):
                best = extended2

    # Strategy 2: random restart greedy on [0, 10000]
    while time.time() < deadline:
        candidates = list(range(10001))
        random.shuffle(candidates)
        S = _greedy_sidon(candidates)
        if len(S) > len(best):
            best = S

    return sorted(best)
