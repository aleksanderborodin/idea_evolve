"""Test find_optimal_shift on multiple primes and run blocker analysis."""

import sys
import time
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem")

from helpers.singer import find_singer_set
from helpers.core import is_sidon

# Import dev functions
sys.path.insert(0, ".")
from optimal_shift_dev import find_optimal_shift, analyze_blockers


def test_prime(q):
    v = q * q + q + 1
    print(f"\n=== q={q}, v={v}, Singer size={q+1} ===")
    t0 = time.time()
    S = find_singer_set(q)
    t_singer = time.time() - t0
    print(f"  Singer construction: {t_singer:.2f}s, got {len(S)} elements")

    t0 = time.time()
    best_shift, truncated = find_optimal_shift(S, v)
    t_shift = time.time() - t0
    print(f"  Optimal shift search: {t_shift:.2f}s")
    print(f"  Best shift: d={best_shift}")
    print(f"  Truncated size: {len(truncated)}")
    print(f"  Is Sidon: {is_sidon(truncated)}")
    print(f"  Range: [{min(truncated)}, {max(truncated)}]")

    # Count shifts that preserve all elements
    full_count = 0
    shift_counts = {}
    for d in range(v):
        cnt = sum(1 for s in S if (s + d) % v <= 10000)
        shift_counts[d] = cnt
        if cnt == len(S):
            full_count += 1

    max_possible = max(shift_counts.values())
    print(f"  Shifts preserving all {len(S)}: {full_count}/{v} ({100*full_count/v:.1f}%)")
    print(f"  Max elements in [0, 10000] for any shift: {max_possible}")

    # Distribution of shift counts
    from collections import Counter
    dist = Counter(shift_counts.values())
    print(f"  Shift count distribution (top 5):")
    for cnt, num_shifts in sorted(dist.items(), reverse=True)[:5]:
        print(f"    {cnt} elements: {num_shifts} shifts")

    # Gap analysis
    gaps = []
    for i in range(len(S)):
        next_idx = (i + 1) % len(S)
        if next_idx == 0:
            gap = (S[0] + v) - S[-1]
        else:
            gap = S[next_idx] - S[i]
        gaps.append(gap)
    max_gap = max(gaps)
    avg_gap = sum(gaps) / len(gaps)
    print(f"  Max consecutive gap (cyclic): {max_gap}")
    print(f"  Avg gap: {avg_gap:.1f}")
    print(f"  v - N = {v - 10000} (elements that 'wrap around')")
    print(f"  Window needed for all elements: v - max_gap = {v - max_gap}")

    return truncated


# Test all primes of interest
for q in [97, 101, 103, 107, 109]:
    test_prime(q)

# Blocker analysis on q=101 truncated set
print("\n\n=== Blocker Analysis (q=101, truncated to 102 elements) ===")
q = 101
v = q * q + q + 1
S = find_singer_set(q)
_, truncated = find_optimal_shift(S, v)

t0 = time.time()
blockers = analyze_blockers(truncated, N=10000)
t_block = time.time() - t0
print(f"Blocker analysis took: {t_block:.2f}s")

if blockers:
    min_b = min(blockers.values())
    max_b = max(blockers.values())
    avg_b = sum(blockers.values()) / len(blockers)
    print(f"Non-members: {len(blockers)}")
    print(f"Min blockers: {min_b}")
    print(f"Max blockers: {max_b}")
    print(f"Avg blockers: {avg_b:.1f}")

    # Distribution
    from collections import Counter
    dist = Counter(blockers.values())
    print("Blocker count distribution:")
    for count in sorted(dist.keys()):
        print(f"  {count} blockers: {dist[count]} non-members")

    # Elements with fewest blockers
    sorted_blockers = sorted(blockers.items(), key=lambda x: x[1])
    print(f"\nTop 10 easiest-to-add elements:")
    for elem, cnt in sorted_blockers[:10]:
        print(f"  element {elem}: {cnt} blockers")
