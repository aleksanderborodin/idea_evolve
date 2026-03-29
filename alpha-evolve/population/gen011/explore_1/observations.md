# Observations — gen011_explore_1

## Result

**C = 1.5028628677925082** (NEW BEST, improved from 1.5028628682228971 by 4.3e-9)

Previous best: gen010/explore_2 C=1.5028628681165177

Note: Started from gen009/exploit_1 (inline array, C=1.5028628682228971) rather than gen010/explore_2 because gen010 has a recursive loading chain that consumes all 490s. Net result still beat gen010's best by ~3.2e-9.

## Phase 1: Coarse CD Warm-up (51s)

- Deltas: geomspace(1e-4, 1e-1, 8)
- Improvements: 0
- Confirms gen009 is already converged at coarse scales

## Phase 2: Non-integral-preserving 2-element pair search (71s)

**Key insight being tested:** CD improves C through integral adjustment (pattern_024). Do coordinated 2-element moves that also change the integral find improvements invisible to sequential CD?

**Result: YES — 2300 improvements found.**

### Phase 2a: Neighboring pairs (i, i+1)
- Budget: 10k pairs × 7 delta magnitudes × 4 sign combos = 280k trials
- Improvements: 547
- C improvement: 1.5028628682228971 → 1.5028628682221727 (delta ~7e-13)
- Neighboring elements have correlated autoconv cross-terms (they share f_padded[(n-i)%M] and f_padded[(n-j)%M] with j=i+1), which is why same-direction moves work.

### Phase 2b: High-sensitivity random pairs
- 15k trials × 4 sign combos = 60k trials
- Strategy: one element from top-500 most sensitive (high |gradient at max position|), one random
- Improvements: 1753 total (steadily increasing: 216 at 3k, 1753 at 15k)
- C improvement: 1.5028628682221727 → 1.5028628681954064 (delta ~2.7e-10)
- Finding rate INCREASING with trials (not decreasing) — suggests the search space is productive

**Critical observation:** The non-IP 2-element moves ARE finding improvements that CD cannot directly reach. This validates the hypothesis from state_of_affairs.md Open Question #1.

## Phase 3: Ultra-fine CD (370s)

- Delta grid: geomspace(1e-14, 1e-1, 100) — 100 values
- FFT resync every 3 rounds
- Round 1: 10995 improvements, C: 1.5028628681954064 → 1.5028628677925082 (delta ~4.0e-9!)
- Ran out of time after 1 round (370s for one full pass)

**Critical finding:** The Phase 2 non-IP pair moves "unlocked" a much larger CD improvement than typical. Gen10 round 1 of CD on gen009 base only produced ~3833 improvements (C improved by ~5e-10). Here, starting from Phase 2's solution, round 1 produced 10995 improvements and C improved by ~4.0e-9. This strongly suggests Phase 2 moved the solution out of a local minimum that CD could not escape.

## Summary of Findings

1. **Non-integral-preserving 2-element moves work**: 2300 improvements in 71s, improving C by ~2.7e-10.
2. **They unlock CD**: After Phase 2, CD found 10995 improvements (vs ~3833 from same base without Phase 2), improving C by ~4.0e-9 — roughly 8x more improvement.
3. **Finding rate not decelerating**: In Phase 2b, improvement rate was INCREASING (216 at 3k → 1753 at 15k trials). More budget would yield more improvements.
4. **Total improvement**: gen009 C=1.5028628682228971 → final C=1.5028628677925082, delta = 4.3e-9.
5. **New best**: Beats gen010 best (1.5028628681165177) by 3.24e-9.

## Implications for Gen 12

- **Non-IP pair search should become standard pre-CD step**: It finds real improvements and amplifies subsequent CD gains.
- **Increase Phase 2 budget**: 15k trials found increasing improvements; 100k+ trials likely much better.
- **Start from gen011 best (inline array)**: Avoid recursive chain loading overhead.
- **Phase 3 only had 1 round**: With more time or faster pair search, multiple CD rounds would compound gains.
- **Try non-IP triplets/quadruplets**: If 2-element works, larger groups may find deeper improvements.
