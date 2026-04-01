# fitness: 616
"""
PGL(2,7) orbit approach for M(8,5).

PGL(2,7) = projective linear group over GF(7) acting on P^1(GF(7)) = {0,...,6,∞}.
We identify {0,...,7} with {0,...,6,∞} (7 = ∞).

Group order: |PGL(2,7)| = 7*(7-1)*(7+1) = 336.
Number of orbits: 40320 / 336 = 120.

Strategy:
1. Implement all 336 PGL(2,7) elements as permutations of {0,...,7}
2. Compute 120 orbits of S_8 under left-composition action
3. Check within-orbit distances (must all be ≥ 5 to form a valid code)
4. Build orbit compatibility graph
5. Find max clique

If a single orbit has all pairs at distance ≥ 5 and size 336, that alone beats 616.
"""

import numpy as np
from itertools import permutations as iperms
from helpers.compat import build_bucket_ids, fast_compatible_mask


def pgl27_elements():
    """Return all 336 elements of PGL(2,7) as permutations of {0,...,7}.
    
    Acts on P^1(GF(7)) = {0,1,2,3,4,5,6,7} where 7 = infinity.
    Mobius transformation: x -> (ax+b)/(cx+d) over GF(7), det != 0.
    Two matrices are equivalent if one is a nonzero scalar multiple of the other mod 7.
    """
    p = 7
    INF = 7  # our representation of infinity
    elements = []
    seen = set()
    
    for a in range(p):
        for b in range(p):
            for c in range(p):
                for d in range(p):
                    det = (a*d - b*c) % p
                    if det == 0:
                        continue
                    # Normalize by scaling so that the first nonzero element is 1
                    # This gives canonical representatives for PGL
                    entry = (a, b, c, d)
                    # Find canonical form: divide all by first nonzero entry mod p
                    for x in entry:
                        if x != 0:
                            inv = pow(x, p-2, p)
                            norm = tuple((xi * inv) % p for xi in entry)
                            break
                    if norm in seen:
                        continue
                    seen.add(norm)
                    
                    # Build permutation of {0,...,7}
                    perm = []
                    for x in range(p + 1):  # 0..7 where 7=inf
                        if x == INF:
                            # inf -> a/c (if c != 0) else inf
                            if c == 0:
                                perm.append(INF)
                            else:
                                perm.append((a * pow(c, p-2, p)) % p)
                        else:
                            denom = (c*x + d) % p
                            if denom == 0:
                                perm.append(INF)
                            else:
                                perm.append((a*x + b) * pow(denom, p-2, p) % p)
                    
                    perm = tuple(perm)
                    # Verify it's a valid permutation
                    if len(set(perm)) == p + 1:
                        elements.append(np.array(perm, dtype=np.int8))
    
    return np.array(elements, dtype=np.int8)


def pgl27_orbits(all_perms, pgl):
    """Partition S_8 into orbits under left-composition with PGL(2,7).
    
    Left action: h . pi = h(pi(x)) for all x (apply pi first, then h).
    """
    N = len(all_perms)
    perm_to_idx = {tuple(p.tolist()): i for i, p in enumerate(all_perms)}
    visited = np.zeros(N, dtype=bool)
    orbits = []
    
    for start in range(N):
        if visited[start]:
            continue
        pi = all_perms[start]
        # Compute h(pi(x)) for each h in PGL
        orbit = pgl[:, pi]  # (|PGL|, 8) — left-compose each h with pi
        # Mark visited
        for row in orbit:
            key = tuple(row.tolist())
            if key in perm_to_idx:
                visited[perm_to_idx[key]] = True
        orbits.append(orbit)
    
    return orbits


def check_orbit_internal(orbit, d=5):
    """Check that all pairs within an orbit have distance >= d."""
    K = len(orbit)
    for i in range(K):
        dists = np.sum(orbit[i] != orbit[i+1:], axis=1)
        if len(dists) > 0 and np.min(dists) < d:
            return False
    return True


def orbit_compat_graph(orbits, pgl, d=5):
    """Build compatibility graph between orbits (same logic as AGL).
    
    Two orbits are compatible iff all pairs between them have distance >= d.
    Equivalent to: min_{h in PGL} hamming(h(rep_i), rep_j) >= d.
    """
    n = len(orbits)
    # Get canonical reps
    reps = np.empty((n, 8), dtype=np.int8)
    for i, orbit in enumerate(orbits):
        sorted_idx = np.lexsort(orbit[:, ::-1].T)
        reps[i] = orbit[sorted_idx[0]]
    
    # All PGL-translates of each rep (= the orbit itself, reordered by pgl action)
    all_translates = np.empty((n, len(pgl), 8), dtype=np.int8)
    for i in range(n):
        all_translates[i] = pgl[:, reps[i]]
    
    compat = np.ones((n, n), dtype=bool)
    np.fill_diagonal(compat, False)
    
    for i in range(n):
        remaining = reps[i+1:]
        if len(remaining) == 0:
            break
        dists = np.sum(all_translates[i][:, np.newaxis, :] != remaining[np.newaxis, :, :], axis=2)
        min_dists = dists.min(axis=0)
        incompat = min_dists < d
        compat[i, i+1:][incompat] = False
        compat[i+1:, i][incompat] = False
    
    return compat


def greedy_clique(compat, start):
    clique = [start]
    cands = list(np.where(compat[start])[0])
    while cands:
        scored = [(c, sum(1 for c2 in cands if compat[c, c2])) for c in cands]
        scored.sort(key=lambda x: -x[1])
        v = scored[0][0]
        clique.append(v)
        cands = [c for c in cands if compat[v, c]]
    return clique


def entrypoint():
    print("Generating all 40320 permutations...")
    all_perms = np.array(list(iperms(range(8))), dtype=np.int8)
    
    print("Computing PGL(2,7) elements...")
    pgl = pgl27_elements()
    print(f"  PGL(2,7) has {len(pgl)} elements (expected 336)")
    
    print("Computing orbits...")
    orbits = pgl27_orbits(all_perms, pgl)
    print(f"  {len(orbits)} orbits (expected ~120)")
    
    # Check orbit sizes and internal distances
    sizes = [len(o) for o in orbits]
    print(f"  Orbit sizes: min={min(sizes)}, max={max(sizes)}, total={sum(sizes)}")
    
    # Check which orbits are internally valid (all pairs distance >= 5)
    valid_orbits = []
    print("  Checking internal validity of orbits...")
    for i, orbit in enumerate(orbits):
        if check_orbit_internal(orbit, d=5):
            valid_orbits.append(i)
    print(f"  {len(valid_orbits)} orbits are internally valid (all internal pairs dist >= 5)")
    
    if not valid_orbits:
        # Fall back to AGL(1,8) 616-code
        print("  No valid PGL orbits — falling back to AGL 616")
        from helpers.agl18 import agl18_max_clique_code
        return agl18_max_clique_code()
    
    # If any orbit alone beats 616, just return the largest valid one
    best_single = max(valid_orbits, key=lambda i: len(orbits[i]))
    best_single_size = len(orbits[best_single])
    print(f"  Best single valid orbit: {best_single_size} perms")
    
    # Build compatibility graph restricted to valid orbits
    valid_orbit_list = [orbits[i] for i in valid_orbits]
    print("  Building orbit compatibility graph...")
    compat = orbit_compat_graph(valid_orbit_list, pgl, d=5)
    degrees = compat.sum(axis=1)
    print(f"  Graph degree: min={degrees.min()}, max={degrees.max()}, avg={degrees.mean():.1f}")
    
    # Greedy clique search
    order = np.argsort(-degrees)
    best_clique = []
    for sv in order[:100]:  # try top 100 by degree
        clique = greedy_clique(compat, int(sv))
        if len(clique) > len(best_clique):
            best_clique = clique
            print(f"  New best clique: {len(clique)} orbits = {sum(len(valid_orbit_list[c]) for c in clique)} perms")
    
    if not best_clique:
        # Return best single orbit
        return orbits[best_single].astype(np.int32)
    
    code_parts = [valid_orbit_list[c] for c in best_clique]
    full_code = np.vstack(code_parts).astype(np.int32)
    print(f"\nFinal code size: {len(full_code)}")
    
    # If PGL result beats 616, great. Otherwise compare to AGL.
    if len(full_code) < 616:
        print("  PGL result below 616 — using AGL 616 instead")
        from helpers.agl18 import agl18_max_clique_code
        return agl18_max_clique_code()
    
    return full_code
