# fitness: TBD
"""
Target 100 elements: start from 99-element set (found by sol02) and systematically try
to reach 100 via structured perturbation.

Key insight: Singer set is saturated (all diffs 1..9506 used). The 99-element set
found by perturbing it has some "slack" — not all diffs are used, so there may be
a 100th element that fits.

Strategy:
1. Recompute the 99-element solution from sol02
2. Find all candidate elements that conflict with the 99-set and WHY
3. For each candidate x, remove the minimal set of elements that block x, then try to fill back
4. Accept if net size ≥ 100
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


def _make_diffs(S):
    S = sorted(S)
    ud = {}  # diff -> (i, j)
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            ud[S[j] - S[i]] = (S[i], S[j])
    return ud


def _greedy_sidon_from(seed, candidates):
    """Extend seed (valid Sidon) with elements from candidates."""
    S = list(seed)
    used_diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            used_diffs.add(abs(S[i] - S[j]))

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
    return sorted(S)


def _find_99_set(base, non_singer, rng, deadline):
    """Replicate sol02's logic to find a 99-element set."""
    base_set = set(base)
    best = list(base)

    for _ in range(600):
        if time.time() > deadline:
            break
        removed = [rng.choice(base)]
        seed = sorted(base_set - set(removed))
        cands = rng.sample(non_singer, len(non_singer))
        ext = _greedy_sidon_from(seed, cands)
        ext2 = _greedy_sidon_from(ext, removed)
        if len(ext2) > len(best):
            best = sorted(ext2)
            if len(best) >= 99:
                return best

    for _ in range(400):
        if time.time() > deadline:
            break
        removed = rng.sample(base, 2)
        seed = sorted(base_set - set(removed))
        cands = rng.sample(non_singer, len(non_singer))
        ext = _greedy_sidon_from(seed, cands)
        ext2 = _greedy_sidon_from(ext, removed)
        if len(ext2) > len(best):
            best = sorted(ext2)
            if len(best) >= 99:
                return best

    return best


def _try_reach_100(s99, all_cands, rng, deadline):
    """Given a 99-element set, try to reach 100."""
    s99_set = set(s99)
    best = list(s99)

    # Find which candidates are blocked and by how many elements
    non_s99 = [c for c in all_cands if c not in s99_set]

    # Compute used diffs of s99
    ud = set()
    for i in range(len(s99)):
        for j in range(i + 1, len(s99)):
            ud.add(s99[j] - s99[i])

    # For each non-member, find which elements of s99 block it
    # (i.e., which elements x in s99 have |x - c| in ud or duplicate)
    def blockers(c, S, used_diffs):
        """Which elements of S create a conflict when adding c?"""
        seen = {}
        blocks = []
        for x in S:
            d = abs(c - x)
            if d in used_diffs:
                # Find which pair created this diff
                blocks.append(x)
            elif d in seen:
                blocks.append(x)
                blocks.append(seen[d])
            else:
                seen[d] = x
        return blocks

    # Try: for each candidate x, if it's blocked by few elements, remove those and rebuild
    while time.time() < deadline:
        # Pick random candidate
        c = rng.choice(non_s99)
        blocked_by = []
        seen = {}
        for x in s99:
            d = abs(c - x)
            if d in ud:
                blocked_by.append(x)
            elif d in seen:
                blocked_by.append(x)
                blocked_by.append(seen[d])
            else:
                seen[d] = x

        if len(blocked_by) <= 4:
            # Try removing the blockers and rebuilding
            seed = sorted(s99_set - set(blocked_by))
            # Include c and other candidates
            cands = [c] + rng.sample(list(s99_set & set(blocked_by)) + non_s99, min(200, len(non_s99)))
            # Deduplicate
            seen_c = set(seed)
            cands = [x for x in cands if x not in seen_c]
            ext = _greedy_sidon_from(seed, cands)
            if len(ext) > len(best):
                best = sorted(ext)

    return best


def entrypoint():
    t0 = time.time()
    deadline_99 = t0 + 20   # First 20s: find 99-element set
    deadline_100 = t0 + 115  # Next 95s: try for 100

    rng = random.Random(42)
    base = _singer_set()
    base_set = set(base)
    all_cands = list(range(10001))
    non_singer = [c for c in all_cands if c not in base_set]

    # Phase 1: get 99-element set
    s99 = _find_99_set(base, non_singer, rng, deadline_99)
    best = s99

    # Phase 2: try to reach 100
    if len(s99) >= 99:
        result = _try_reach_100(sorted(s99), all_cands, rng, deadline_100)
        if len(result) > len(best):
            best = result
    else:
        # Fall back to more perturbations
        while time.time() < deadline_100:
            removed = rng.sample(base, rng.randint(1, 5))
            seed = sorted(base_set - set(removed))
            cands = rng.sample(non_singer, len(non_singer))
            ext = _greedy_sidon_from(seed, cands)
            ext2 = _greedy_sidon_from(ext, removed)
            if len(ext2) > len(best):
                best = sorted(ext2)

    return sorted(best)
