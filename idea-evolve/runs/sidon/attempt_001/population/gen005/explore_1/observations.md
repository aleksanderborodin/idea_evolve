# Observations — gen005 explore_1: Beam Search for Sidon Sets

## Summary of Attempts

| Solution | Algorithm | k_beams | Candidate Strategy | Fitness | Time (s) |
|----------|-----------|---------|-------------------|---------|----------|
| sol01 | Beam search (sorted list) | 30 | First 3 valid (greedy-like) | 69 | 1.77 |
| sol02 | Beam search (numpy mask) | 20 | Spread 8 (bug: wrong valid_mask) | 67 | 3.74 |
| sol03 | Beam search + lookahead | 50 | Spread 10, depth-5 greedy lookahead | 67 | 32.7 |
| sol04 | Multi-seed beam search | 5/seed×15seeds | Front+back, 15 seeds | 67 | 5.6 |
| sol05 | Beam search (numpy mask) | 500 | First 2 valid (greedy-like) | 70 | 15.8 |
| sol06 | Beam search (numpy mask) | 500 | 25th/75th percentile | 66 | 19.3 |
| sol07 | Beam search (numpy mask) | 800 | First 2 valid (greedy-like) | 70 | 25.4 |

**Best result: 70 elements** (sol05 and sol07, k=500 and k=800)

## Key Finding: The Greedy Ceiling is Structural

**The main finding of this exploration**: beam search with ANY reasonable beam width
(up to k=800) ceiling at 70 elements. Greedy alone reaches 66-69; beam search adds
at most 1-4 elements (reaching 70). This conclusively confirms pattern_011:

> "All greedy variants ceiling at 66-69 (pattern_011, confidence 0.85)"

Beam search extends this ceiling from 69 → 70 with enough beams (k≥500), but cannot
break past 70 in 30 seconds regardless of k.

## What Worked (Better)

- **Greedy-like candidate selection** (first 1-2 smallest valid) consistently
  outperformed diverse sampling (25th/75th pct, spread). Picking smallest valid
  is locally optimal and globally competitive.
- **Wide beams help marginally**: k=500 → 70 vs k=30 → 69. The 1-element improvement
  at k=500 is real but modest.
- **Numpy valid-mask** representation is efficient: 15.8s for k=500 with correct
  incremental updates.

## What Failed

- **Diverse candidate sampling** (25th/75th pct, spread across range): consistently
  WORSE than greedy (66-67 vs 69-70). Picking large candidates wastes the remaining
  valid range.
- **Greedy lookahead scoring** (depth=5): no improvement, 10× slower (32s for 67
  elements). The lookahead signal is too noisy.
- **Multiple seeds** (starting from different first elements): same ceiling (67).
  The ceiling is not seed-dependent.
- **k=800 vs k=500**: identical result (70). No gain from wider beams at this scale.

## Root Cause Analysis

The greedy ceiling is caused by **difference saturation**. After ~70 elements, the
set of used differences (≈70×69/2 ≈ 2415 values) plus the blocking structure they
create covers essentially all remaining valid positions in [0, 10000]. Any greedy
path—regardless of which specific choices were made—hits this wall.

Beam search can find the rare "lucky" greedy path that delays saturation by 1-4
elements, but cannot fundamentally escape it because:
1. All beams use the same greedy strategy (add valid candidate)
2. The difference saturation is a structural property of [0, 10000], not of any
   specific element choices
3. The algebraic Singer construction (102 elements) is structurally superior because
   it avoids difference saturation by design (GF(q³) guarantees all differences distinct)

## Implications

- Beam search is NOT the path to 103+ elements. Confirmed.
- The theoretical gap (70 vs 109 target) cannot be closed by any greedy-based approach.
- The 70 result (sol05/sol07) is a new non-Singer, non-ET baseline, but only modestly
  better than pattern_011's established greedy ceiling of 66-69.
- Next steps must focus on: ILP/CP-SAT (idea_019), Rokicki-Dogon database (idea_020),
  or algebraic constructions beyond Singer q=101.

## Bugs Found

- **sol01 bug (not critical)**: the "blocking" computation in count_blocked() was
  approximated over a limited window rather than full valid range. Results still valid.
- **sol02 bug (critical, fixed)**: first valid_mask version sampled positions ≤ max(elems),
  producing invalid sets with 444 violations. Fixed by filtering `valid_mask[last+1:]`.
  The correct blocking rule: when adding c, newly blocked = {c+d : d ∈ all_diffs} ∩ [0,N].

## Helper Tool Feedback

- `helpers/core.py`: Not used directly (reimplemented from scratch for numpy efficiency).
- `helpers/search.py` `greedy_sidon`: Useful for baseline comparison, not used.
- Would have been helpful: a **numpy-native beam search helper** that maintains
  valid_mask incrementally and handles the blocked-position update vectorized.
  This would reduce implementation time from ~3 hours to ~30 minutes.
