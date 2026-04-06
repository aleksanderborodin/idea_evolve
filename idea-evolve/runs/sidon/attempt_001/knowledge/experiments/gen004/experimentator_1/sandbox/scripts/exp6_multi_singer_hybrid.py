"""
EXP-6: Multi-Singer Hybrid Test
Tests whether elements from different algebraic constructions (Singer q=101, Singer q=97,
ET p=71) can be combined into a Sidon set larger than 102.

Independent variable: Which construction is used as source for additional elements
Dependent variable: Number of elements that can be added to reduced base
Control: Full 102-element Singer q=101 set (confirmed zero addable elements)
Fixed: N=10000, greedy forward-scan addition
"""
import sys
import os
import time

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem')
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon')

SINGER_SET = [0, 129, 385, 586, 624, 844, 938, 1001, 1008, 1104, 1169, 1183, 1186, 1201, 1212, 1225, 1332, 1420, 1574, 1633, 1679, 1868, 1963, 2075, 2212, 2235, 2337, 2388, 2479, 2489, 2520, 2547, 2613, 2829, 2849, 2854, 3023, 3195, 3578, 3635, 3719, 3793, 3805, 3931, 4007, 4268, 4328, 4456, 4518, 4537, 4571, 4648, 4654, 4721, 4835, 4927, 5002, 5145, 5167, 5366, 5413, 5666, 5699, 5735, 5789, 5839, 6086, 6094, 6134, 6457, 6492, 6537, 6592, 6608, 6636, 6714, 6763, 6919, 7052, 7197, 7199, 7489, 7490, 7599, 7686, 8029, 8093, 8191, 8421, 8506, 8510, 8739, 8776, 8962, 9014, 9075, 9194, 9266, 9627, 9745, 9766, 9775]

N = 10000


def build_diffs(S):
    """Build set of all pairwise positive differences for sorted S."""
    diffs = set()
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            diffs.add(S[j] - S[i])
    return diffs


def can_add_element(S_sorted, used_diffs, c):
    """Check if c can be added to S without violating Sidon property."""
    new_diffs = []
    for x in S_sorted:
        d = abs(c - x)
        if d in used_diffs or d in new_diffs:
            return False, []
        new_diffs.append(d)
    return True, new_diffs


def count_addable(base, candidates):
    """Count how many candidates can be added one-by-one to base (greedy forward scan)."""
    S = sorted(base)
    diffs = build_diffs(S)
    added = []
    for c in sorted(candidates):
        if c in set(S):
            continue
        ok, new_diffs = can_add_element(S, diffs, c)
        if ok:
            added.append(c)
            S.append(c)
            S.sort()
            diffs.update(new_diffs)
    return added


def build_et_set(p, N=10000):
    """Build Erdos-Turan set for prime p in {0,...,N}.

    ET set: S = {(k^2 + k) mod p : k = 0,...,p-1} viewed in Z
    But we need it in {0,...,N}. Standard construction:
    S_ET = { (i*(i+1)) mod p + p*j : for fitting integers }

    Actually the standard Erdos-Turan B_2 sequence in {0,...,N}:
    For prime p, the set S = {2pk + (k^2 mod p) : k=0,...,p-1} works but gives ~p elements in {0,...,2p^2}.

    Simpler: use S = {(i^2 + i) mod (2p+1) : i=0,...,p} — this is a cyclic B_2 in Z_{2p+1}.
    But that's not directly ET.

    Let's use the polynomial construction: S = {i*p + (i^2 mod p) for i in range(p)}.
    This gives p elements in {0,...,p^2+p}.
    """
    # Use: S = {i*p + (i^2 % p) for i in range(p)} — "Bose" construction
    # Elements in range [0, (p-1)*p + (p-1)] = [0, p^2-1]
    S = []
    for i in range(p):
        val = i * p + (i * i % p)
        if val <= N:
            S.append(val)
    return sorted(set(S))


def build_et_standard(p, N=10000):
    """
    Erdős-Turán set: uses B_q sequence from the paper.
    For prime p, construct: a_k = p*k + r_k where r_k = k^2 mod p.
    This is the standard Erdős-Turán construction giving a B_2 set of size p in {0,...,p^2}.
    """
    S = []
    for k in range(p):
        val = p * k + (k * k % p)
        if 0 <= val <= N:
            S.append(val)
    return sorted(S)


def run_exp6():
    print("=" * 60)
    print("EXP-6: Multi-Singer Hybrid Test")
    print("=" * 60)

    singer_101 = sorted(SINGER_SET)
    print(f"Singer q=101: {len(singer_101)} elements, range [{singer_101[0]}, {singer_101[-1]}]")

    # Load Singer q=97
    t0 = time.time()
    from helpers.singer import find_singer_set
    singer_97_full = find_singer_set(97)  # 98 elements in {0..9506}
    print(f"Singer q=97 (full, unshifted): {len(singer_97_full)} elements, range [{singer_97_full[0]}, {singer_97_full[-1]}]")
    print(f"  (Building took {time.time()-t0:.1f}s)")

    # Singer q=97 is in Z_{97^2+97+1} = Z_{9507}. Already fits in N=10000.
    singer_97 = [x for x in singer_97_full if x <= N]
    print(f"Singer q=97 truncated to N={N}: {len(singer_97)} elements")

    # ET set for p=71
    et_71 = build_et_standard(71, N)
    print(f"ET p=71 (Bose construction): {len(et_71)} elements, range [{et_71[0]}, {et_71[-1]}]")

    # Verify ET is actually Sidon
    et_diffs = build_diffs(et_71)
    et_is_sidon = len(et_diffs) == len(et_71) * (len(et_71) - 1) // 2
    print(f"  ET p=71 is Sidon: {et_is_sidon}")

    print()
    print("--- Test 1: Full Singer-102 base, try adding ET-71 elements ---")
    added_to_full = count_addable(singer_101, et_71)
    print(f"  Elements added from ET to full Singer-102: {len(added_to_full)}")
    if added_to_full:
        print(f"  Added elements: {added_to_full[:10]}...")

    print()
    print("--- Test 2: Full Singer-102 base, try adding Singer-97 elements ---")
    added_s97_to_full = count_addable(singer_101, singer_97)
    print(f"  Elements added from Singer-97 to full Singer-102: {len(added_s97_to_full)}")
    if added_s97_to_full:
        print(f"  Added elements: {added_s97_to_full[:10]}...")

    print()
    print("--- Test 3: Reduced Singer-101 bases, try adding ET-71 elements ---")
    results_et = {}
    for k in [90, 80, 70, 60, 50, 40]:
        base = singer_101[:k]
        added = count_addable(base, et_71)
        total = k + len(added)
        results_et[k] = (len(added), total)
        print(f"  Base Singer-102[:{k}] + ET-71: added {len(added)}, total={total}")

    print()
    print("--- Test 4: Reduced Singer-101 bases, try adding Singer-97 elements ---")
    results_s97 = {}
    for k in [90, 80, 70, 60, 50, 40]:
        base = singer_101[:k]
        added = count_addable(base, singer_97)
        total = k + len(added)
        results_s97[k] = (len(added), total)
        print(f"  Base Singer-102[:{k}] + Singer-97: added {len(added)}, total={total}")

    print()
    print("--- Test 5: ET-71 base, try adding Singer-101 elements ---")
    added_s101_to_et = count_addable(et_71, singer_101)
    print(f"  Elements added from Singer-101 to ET-71 base ({len(et_71)} elems): {len(added_s101_to_et)}")
    print(f"  Total: {len(et_71) + len(added_s101_to_et)}")
    if added_s101_to_et:
        print(f"  Added elements: {added_s101_to_et[:10]}...")

    print()
    print("--- Test 6: Singer-97 base, try adding Singer-101 elements ---")
    added_s101_to_s97 = count_addable(singer_97, singer_101)
    print(f"  Elements added from Singer-101 to Singer-97 base ({len(singer_97)} elems): {len(added_s101_to_s97)}")
    print(f"  Total: {len(singer_97) + len(added_s101_to_s97)}")

    print()
    print("--- Test 7: Reduce Singer-101 base, fill from ET-71, then fill from Singer-97 ---")
    best_hybrid = 0
    best_config = None
    for k in [70, 75, 80, 85]:
        base = list(singer_101[:k])
        # Step 1: add ET elements
        added1 = count_addable(base, et_71)
        combined = base + added1
        # Step 2: try adding Singer-97 to that combined set
        added2 = count_addable(combined, singer_97)
        total = len(combined) + len(added2)
        if total > best_hybrid:
            best_hybrid = total
            best_config = (k, len(added1), len(added2), total)
        print(f"  Singer-101[:{k}] -> +{len(added1)} ET-71 -> +{len(added2)} Singer-97 = {total}")

    print()
    print(f"Best hybrid total: {best_hybrid}")
    if best_hybrid > 102:
        print("*** BREAKTHROUGH: Hybrid exceeds 102! ***")
    else:
        print("No hybrid exceeds 102.")

    return {
        'singer_101_size': len(singer_101),
        'singer_97_size': len(singer_97),
        'et_71_size': len(et_71),
        'et_71_is_sidon': et_is_sidon,
        'added_et_to_full': len(added_to_full),
        'added_s97_to_full': len(added_s97_to_full),
        'reduced_base_et': results_et,
        'reduced_base_s97': results_s97,
        'best_hybrid': best_hybrid,
    }


if __name__ == '__main__':
    results = run_exp6()
