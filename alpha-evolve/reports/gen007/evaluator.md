# Evaluator Report — Generation 7

**strategic_shift: false**

## Summary

Generation 7 produced 7 valid solutions, all from the TTT-Discover 30k starting point.
New overall best: **C = 1.5028628688924555** (explore_1/sol01, triplet perturbation),
improving on gen 6 best by -3.578e-9. Four solutions improved over the gen 6 baseline;
three returned unchanged (LP attempts). The generation confirms incremental progress and
introduces triplet perturbation as a new technique (idea_021), while demonstrating that
single-element coordinate descent has essentially converged (pattern_012) and LP refinement
faces a fundamental obstacle (pattern_013).

## 1. What did I try?

### Score collection
All 7 solutions had `.score` sidecar files. No re-evaluation needed.

### Analysis
Read all 4 agent debrief reports (exploit_1, exploit_2, explore_1, full_1), architect report,
and experimentator report. Analyzed solution strategies, cross-referenced with existing
knowledge base (20 ideas, 11 patterns, 3 clusters).

### Knowledge updates
- Created idea_021 (triplet perturbation, confidence 0.65)
- Created pattern_012 (coord descent convergence decay)
- Created pattern_013 (LP plateau obstacle)
- Updated idea_019 (coord descent convergence documented, confidence 0.80→0.85)
- Updated idea_020 (LP demoted to DISPUTED, confidence 0.35→0.2)
- Updated cluster_001 (added idea_021, new best score)
- Updated cluster_003 (new best score, LP status)
- Updated solution-idea map (7 new entries)
- Updated coverage matrix (5 new rows, 2 new dead ends, revised unexplored priorities)

## 2. What information did I lack?

- **Per-strategy breakdown of triplet improvements.** explore_1 didn't log which of the 4
  selection strategies produced improvements. This would inform future triplet search design.
- **Whether coord descent + triplet interleaving helps.** No agent tested this. It's the
  highest-priority untested combination.
- **Autoconvolution plateau statistics at intermediate resolutions (N=5000-10000).** This
  would determine LP feasibility at those scales.

## 3. What given facts might be wrong or outdated?

- **fact_002** states "best known bounds 1.28 ≤ C ≤ 1.5098, target C ≤ 1.5053." Current
  best is 1.50286, target beaten since gen 3. Should be updated.
- **idea_019** previously stated "improvement rate still 1800/round after 3 full-array
  passes. The coordinate-wise optimum has NOT been reached." This was premature — gen 7
  shows sharp convergence. Updated in output.
- **idea_020** stated "engineering difficulty is higher than anticipated." The engineering
  is now solved; the problem is fundamental (plateau structure). Updated in output.
- **State of Affairs (gen 6)** listed "Extended coordinate descent (10+ more full-array
  rounds)" as the top priority. This is now low-value — coord descent is converging.
  Triplet perturbation and interleaving should replace it as the active frontier.

## 4. Was the State of Affairs accurate?

Mostly accurate for gen 7 planning. It correctly identified coordinate descent as the
active frontier and LP refinement as high-priority. Two inaccuracies:

1. **"Improvement rate is still 1800/round — how far can this go?"** — Answer: not much
   further. Sharp convergence observed in gen 7. The SoA was overly optimistic about
   remaining coordinate descent headroom.

2. **"LP at reduced resolution (N=2000) is the next attempt"** — This was attempted and
   failed. The SoA didn't anticipate the resolution sensitivity of LP descent directions.

## 5. What would I do differently with more or different context?

- **Incorporate plateau statistics as a fact file.** The ~6500 near-max points and ~7e-21
  gap between 1st and 2nd autoconv positions are critical structural data that should be
  in a fact file, not buried in agent reports.

- **Flag the coord descent convergence claim in idea_019 earlier.** The gen 6 claim of
  "NOT converging" should have been tagged as uncertain pending gen 7 confirmation.

## 6. Specific experiments to run

### Experiment 1: Interleaved triplet + coordinate descent (HIGHEST PRIORITY)
- Start from gen007_explore_1_sol01 (C=1.5028628689)
- Run 3 rounds of full-array coordinate descent
- Then 30k triplet trials
- Then 3 more rounds of coord descent
- Repeat until both converge simultaneously
- **Hypothesis:** Each method unlocks improvements for the other

### Experiment 2: Momentum-enhanced triplet search
- After each accepted triplet move, immediately retry same triplet with 2x step
- Also retry with permutations of the same 3 elements
- Try nearby triplets (replace one element with neighbor)
- **Hypothesis:** Improvements cluster spatially and directionally

### Experiment 3: Quadruplet perturbation (d1+d2+d3+d4=0)
- 4-element integral-preserving moves with gradient-guided selection
- If triplets work where pairs don't, quadruplets may work where triplets exhaust
- **Hypothesis:** Higher-order moves access more of the improvement landscape

### Experiment 4: LP plateau analysis at intermediate resolutions
- Load best.py, downsample to N=5000, 8000, 10000
- Count tight constraints at epsilon_rel = 1e-6, 1e-5, 1e-4
- If plateau is <500 points at N=5000, LP might be tractable AND direction might transfer
- **Hypothesis:** Sweet spot exists between N=2000 (too coarse) and N=30000 (too many tight)

### Experiment 5: Triplet strategy A/B/C/D breakdown
- Run 10k triplets per strategy separately, log improvement count and magnitude
- Identify dominant strategy, then invest 50k trials in the winner
- **Hypothesis:** Mass redistribution (large→small) dominates random selection

## 7. What surprised me?

1. **Triplets found 160 improvements where pairs found 1.** The mathematical explanation
   (triplets have nonzero gradient at the pair-optimal point) is clean. This was the
   top coverage matrix suggestion and it delivered.

2. **Coordinate descent converged much faster than expected.** Gen 6 reported "NOT converging"
   with 1800/round. Starting from the same array, gen 7 agents found sharp exponential decay.
   The gen 6 report described rounds 1-3 of a fresh full-array scan; gen 7 continued from
   that output and found rounds 4-6 had 96.6% fewer improvements.

3. **LP engineering is solved but the idea is fundamentally blocked.** The expectation was
   "fix the engineering and LP will work." Instead, the plateau structure makes LP intractable
   regardless of implementation quality.

4. **AlphaEvolve N=600 is a true coordinate-wise minimum.** ZERO improvements with any delta.
   The LP-guided memetic algorithm that produced it was already thorough at small N.

5. **Three independent coordinate descent agents found different improvement counts (156 vs
   257 vs 6551) from the same starting point.** Different delta grids and scan orderings
   produce different results. The greedy coordinate descent path is highly sensitive to
   implementation details, even though the final convergence point is similar.

## 8. Helper tools feedback

I did not use helper tools directly (evaluator reads scores and knowledge, doesn't run code).
Based on agent reports:

- **compute_c_f64**: Used by all agents, no issues reported. Essential ground truth.
- **incremental_autoconv_update** (new, experimentator gen 7): Not available to gen 7 agents
  (delivered simultaneously). All 3 coord descent agents reimplemented it. Will save time
  in gen 8.
- **cross_convolution_f64** (new): Not used by any gen 7 agent.
- **lp_matrix** (new): Not used by gen 7 full_1 (which reimplemented LP construction). Would
  have saved significant time if available earlier.
- **Missing helper (multiple agents request):** `coordinate_descent.py` — a full coordinate
  descent loop using incremental_update. Would standardize delta grids and scan ordering
  across agents.
- **Missing helper (exploit_1 request):** `safe_set_autoconv_update` — track positions near
  autoconv max, only check those for max computation. 3x speedup.
