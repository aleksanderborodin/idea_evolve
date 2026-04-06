"""
EXP-4: Unused Difference Spectrum Analysis
Tests the algebraic structure of differences NOT used by the Singer q=101 set.

Independent variable: structural analysis of free differences
Dependent variable: algebraic patterns and trading opportunities
Control: Singer q=101 set (102 elements, 5151 pairwise differences)
Fixed: N=10000
"""
import sys
import math
import collections
import time

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem')
sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon')

SINGER_SET = [0, 129, 385, 586, 624, 844, 938, 1001, 1008, 1104, 1169, 1183, 1186, 1201, 1212, 1225, 1332, 1420, 1574, 1633, 1679, 1868, 1963, 2075, 2212, 2235, 2337, 2388, 2479, 2489, 2520, 2547, 2613, 2829, 2849, 2854, 3023, 3195, 3578, 3635, 3719, 3793, 3805, 3931, 4007, 4268, 4328, 4456, 4518, 4537, 4571, 4648, 4654, 4721, 4835, 4927, 5002, 5145, 5167, 5366, 5413, 5666, 5699, 5735, 5789, 5839, 6086, 6094, 6134, 6457, 6492, 6537, 6592, 6608, 6636, 6714, 6763, 6919, 7052, 7197, 7199, 7489, 7490, 7599, 7686, 8029, 8093, 8191, 8421, 8506, 8510, 8739, 8776, 8962, 9014, 9075, 9194, 9266, 9627, 9745, 9766, 9775]

N = 10000


def build_diffs_set(S):
    """Build set of all pairwise positive differences."""
    diffs = set()
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            diffs.add(S[j] - S[i])
    return diffs


def blocker_analysis(S, N=10000):
    """
    For each non-member c, find which S elements block it and how many.
    An element s blocks c if |c-s| is already in the difference set of S.
    Returns: dict mapping c -> list of blocking elements
    """
    S_set = set(S)
    used_diffs = build_diffs_set(S)

    blockers = {}
    for c in range(N+1):
        if c in S_set:
            continue
        blocking = []
        for s in S:
            d = abs(c - s)
            if d in used_diffs:
                blocking.append(s)
        blockers[c] = blocking
    return blockers, used_diffs


def run_exp4():
    print("=" * 60)
    print("EXP-4: Unused Difference Spectrum Analysis")
    print("=" * 60)

    S = sorted(SINGER_SET)
    S_set = set(S)
    n = len(S)
    print(f"Singer q=101 set: {n} elements")

    # Step 1: Compute pairwise differences
    t0 = time.time()
    used_diffs = build_diffs_set(S)
    n_used = len(used_diffs)
    n_expected = n * (n-1) // 2
    print(f"Pairwise differences: {n_used} (expected {n_expected})")
    assert n_used == n_expected, "Singer set should have all distinct differences!"
    print(f"  All pairwise differences are distinct (confirmed Sidon property)")

    # Step 2: Free differences
    all_possible = set(range(1, N+1))
    free_diffs = all_possible - used_diffs
    n_free = len(free_diffs)
    print(f"\nFree differences (not used): {n_free} out of {N}")
    print(f"Usage ratio: {n_used/N*100:.1f}% of {N} possible differences used")

    # Step 3: Distribution analysis of free differences
    free_sorted = sorted(free_diffs)
    print(f"\n--- Free Difference Distribution ---")

    # Bucket analysis (10 buckets)
    bucket_size = N // 10
    buckets = [0] * 10
    for d in free_diffs:
        buckets[(d-1) // bucket_size] += 1
    print("Free differences per decile:")
    for i, cnt in enumerate(buckets):
        lo = i * bucket_size + 1
        hi = (i+1) * bucket_size
        total_in_bucket = bucket_size
        used_in_bucket = total_in_bucket - cnt
        print(f"  [{lo:5d}-{hi:5d}]: {cnt} free, {used_in_bucket} used ({used_in_bucket/total_in_bucket*100:.1f}% used)")

    # Gap analysis of free differences (are they clustered?)
    gaps = []
    prev = 0
    for d in free_sorted:
        gaps.append(d - prev - 1)  # number of used differences before this free one
        prev = d
    print(f"\nFree diff gap stats (gaps between consecutive free diffs):")
    gap_sorted = sorted(gaps)
    print(f"  Min gap: {min(gaps)}")
    print(f"  Max gap: {max(gaps)}")
    print(f"  Mean gap: {sum(gaps)/len(gaps):.2f}")
    print(f"  Runs of 1 (consecutive free): {sum(1 for g in gaps if g==0)}")

    # Step 4: Consecutive runs of free differences
    runs = []
    run_len = 1
    for i in range(1, len(free_sorted)):
        if free_sorted[i] == free_sorted[i-1] + 1:
            run_len += 1
        else:
            runs.append(run_len)
            run_len = 1
    runs.append(run_len)
    long_runs = [(r, free_sorted[sum(runs[:i])]) for i, r in enumerate(runs) if r >= 5]
    print(f"\nLongest consecutive runs of free diffs (len>=5): {len(long_runs)} runs")
    for r, start in sorted(long_runs, reverse=True)[:10]:
        print(f"  Length {r} starting at {start}")

    # Step 5: Blocker analysis
    print(f"\n--- Blocker Analysis ---")
    t1 = time.time()
    blockers, _ = blocker_analysis(S, N)
    print(f"(Computed in {time.time()-t1:.1f}s)")

    blocker_counts = {c: len(b) for c, b in blockers.items()}
    counts_sorted = sorted(blocker_counts.values())
    min_blockers = min(counts_sorted)
    max_blockers = max(counts_sorted)
    mean_blockers = sum(counts_sorted) / len(counts_sorted)

    print(f"Non-members: {len(blockers)}")
    print(f"Blocker count stats:")
    print(f"  Min: {min_blockers}")
    print(f"  Max: {max_blockers}")
    print(f"  Mean: {mean_blockers:.2f}")

    # Distribution of blocker counts
    count_dist = collections.Counter(counts_sorted)
    print(f"\nDistribution of blocker counts (count: # of non-members):")
    for cnt in sorted(count_dist.keys())[:20]:
        print(f"  {cnt} blockers: {count_dist[cnt]} non-members")

    # Find the best candidates (fewest blockers)
    best_candidates = sorted(blocker_counts.items(), key=lambda x: x[1])[:20]
    print(f"\nBest 20 non-members (fewest blockers):")
    for c, bc in best_candidates:
        blocking_elems = blockers[c]
        print(f"  c={c}: {bc} blockers = {blocking_elems[:10]}{'...' if len(blocking_elems) > 10 else ''}")

    # Step 6: Trading analysis
    print(f"\n--- Trading Analysis ---")
    print("For best candidates (fewest blockers), check if removing blocking elements")
    print("would allow adding more elements than removed.")

    # For each best candidate, find which Singer elements block it
    # Then check: if we remove those blockers, what happens?
    best_c, min_bc = best_candidates[0]
    print(f"\nFocusing on c={best_c} ({min_bc} blockers):")
    blocking_of_best = set(blockers[best_c])
    print(f"  Blocking elements: {sorted(blocking_of_best)}")

    # If we remove all blockers of best_c, can we add best_c plus others?
    S_reduced = [x for x in S if x not in blocking_of_best]
    S_reduced_set = set(S_reduced)
    diffs_reduced = build_diffs_set(S_reduced)

    # Now count how many elements can be added to S_reduced
    addable_after_removal = []
    for c in range(N+1):
        if c in S_reduced_set:
            continue
        can_add = True
        new_diffs = set()
        for x in S_reduced:
            d = abs(c - x)
            if d in diffs_reduced or d in new_diffs:
                can_add = False
                break
            new_diffs.add(d)
        if can_add:
            addable_after_removal.append(c)

    print(f"  After removing {len(blocking_of_best)} blockers ({len(S_reduced)} elements remain):")
    print(f"  Elements that become addable: {len(addable_after_removal)}")
    print(f"  Net change: remove {len(blocking_of_best)}, gain {len(addable_after_removal)}")
    if len(addable_after_removal) > len(blocking_of_best):
        total_new = len(S_reduced) + len(addable_after_removal)
        print(f"  *** NET GAIN! New set size could be {total_new} ***")
    else:
        print(f"  No net gain from trading.")
    if addable_after_removal[:5]:
        print(f"  Addable elements (first 5): {addable_after_removal[:5]}")

    # More targeted: find minimal removal set
    print(f"\n--- Minimal Removal Trading ---")
    # For the top 5 best candidates, try removing only 1 element to free them up
    print("Can we add a non-member by removing just 1 Singer element?")
    for c, bc in best_candidates[:10]:
        blocking = blockers[c]
        if len(blocking) == 1:
            # Removing just 1 element would free c
            s_remove = blocking[0]
            # Check if this removal allows adding c AND anything else
            S2 = [x for x in S if x != s_remove]
            d2 = build_diffs_set(S2)
            ok2 = True
            new2 = set()
            for x in S2:
                d = abs(c - x)
                if d in d2 or d in new2:
                    ok2 = False
                    break
                new2.add(d)
            if ok2:
                print(f"  Remove {s_remove}, add {c}: net 0 (still {len(S)} elements)")

    # Check: with 2 removals
    print("\nCan we remove 2 elements and add 3+ new ones?")
    from helpers.core import can_add as can_add_helper

    # For each pair of elements in the 20 best candidates' blocker sets, check
    # This is O(n^2) on the blocker set — manageable
    all_blockers_of_best = set()
    for c, bc in best_candidates[:10]:
        all_blockers_of_best.update(blockers[c])
    all_blockers_list = sorted(all_blockers_of_best)

    best_trade = (0, 2, None, None)  # (net_gain, removed_count, removed, added)
    checked = 0
    for i, s1 in enumerate(all_blockers_list):
        for s2 in all_blockers_list[i+1:]:
            checked += 1
            if checked > 5000:
                break
            S2 = [x for x in S if x != s1 and x != s2]
            d2 = build_diffs_set(S2)
            addable = []
            for c in range(N+1):
                if c in set(S2):
                    continue
                ok = True
                nd = set()
                for x in S2:
                    d = abs(c - x)
                    if d in d2 or d in nd:
                        ok = False
                        break
                    nd.add(d)
                if ok:
                    addable.append(c)
                if len(addable) > 5:
                    break
            net = len(addable) - 2
            if net > best_trade[0]:
                best_trade = (net, 2, (s1, s2), addable[:5])

        if checked > 5000:
            break

    print(f"  Best trade found (checked {checked} pairs): net gain = {best_trade[0]}")
    if best_trade[0] > 0:
        print(f"  Remove {best_trade[2]}, gain at least {best_trade[1]+best_trade[0]} elements")
        print(f"  Addable elements: {best_trade[3]}")

    print(f"\nTotal elapsed: {time.time()-t0:.1f}s")

    return {
        'n_used_diffs': n_used,
        'n_free_diffs': n_free,
        'min_blockers': min_blockers,
        'max_blockers': max_blockers,
        'mean_blockers': mean_blockers,
        'best_candidates_top5': best_candidates[:5],
    }


if __name__ == '__main__':
    results = run_exp4()
