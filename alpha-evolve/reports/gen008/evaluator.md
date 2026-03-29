# Evaluator Report — Generation 8

**strategic_shift: false**

## Summary

Generation 8 produced 3 valid solutions from 4 agents (explore_2 ran diagnostic experiments
only). New overall best: **C = 1.5028628684790137** (explore_1/sol01), improving on gen 7's
best by -4.13e-10 via quadruplet perturbation + triplet follow-up. The interleaving hypothesis
(higher-order perturbations unlock lower-order improvement directions) is now confirmed by
two independent agents.

## 1. What did I try?

### Score collection
Read .score sidecar files for all 3 solutions. All scores were pre-verified by evaluate.py
(cached by content hash). No re-evaluation needed.

### Analysis of 4 agent outputs
- **explore_1:** Quadruplet perturbation — 8015 improvements across 4 strategies, then 2523
  triplet follow-up improvements. New idea (idea_022) created.
- **exploit_1:** Single-round coord descent on gen 7's triplet-modified array — 2008 new
  improvements. Confirms interleaving: triplets unlock new coord descent directions.
- **exploit_2:** Momentum-enhanced triplets — 0 improvements in 36k Strategy 1 trials.
  Negative result confirming triplet exhaustion on unmodified gen 7 best.
- **explore_2:** LP plateau analysis (downsampling destroys structure) + FFT padding validation
  (all sizes identical to 1e-15). Two important diagnostic results, no solution produced.
- **experimentator_1:** coordinate_descent.py helper built, small-array tests pass, large-array
  validation incomplete.

### Knowledge updates
- Created 1 new idea (idea_022: quadruplet perturbation)
- Created 3 new patterns (pattern_014: interleaving unlocking; pattern_015: downsampling
  destruction; pattern_016: FFT padding validated)
- Updated 4 existing ideas (idea_021 promoted to established, idea_019 confidence raised,
  idea_014 last_confirmed_gen updated, idea_020 gen 8 data added)
- Updated 2 clusters (cluster_001 and cluster_003)
- Updated solution-idea map with all gen 8 entries
- Updated coverage matrix with gen 8 combinations

### Staleness check
- **pattern_003** (diminishing returns from optimizer steps): last_updated gen 1. Stale but
  remains true — pattern is well-established and unlikely to change.
- **pattern_004** (N=600 outperforms higher N): last_updated gen 1. Stale but still holds for
  gradient descent context. Not relevant to current frontier.
- **pattern_005** (1.509x basin depth): last_updated gen 3. Stale but established fact.
- **pattern_006** (arcsine init dominance): last_updated gen 3. Stale and irrelevant to frontier.
  Consider archiving.
- **idea_006** (analytical constructions): last_confirmed gen 7 (refreshed). Not stale.
- **idea_012** (asymmetry exploitation): last_confirmed gen 3 (5 gens stale). Established
  mathematical fact, unlikely to change, but flagging per staleness policy.

### Experiment consolidation
- Checked `knowledge/experiments/`. Gen 6, 7, 8 experiments present. Gen 6 experiments are
  3 generations old — at the consolidation threshold. Key findings from gen 6 experiments
  are already captured in patterns (pattern_010, pattern_011) and idea updates. No new
  consolidation needed this generation.

## 2. What information did I lack?

- **Per-strategy time-resolved improvement rates** for both triplet (gen 7) and quadruplet
  (gen 8) searches. Only totals were logged, not improvement density over time.
- **The effective safe-set margin** from gen 7 exploit_1's implementation. exploit_1 gen 8
  wasted time discovering that margin=1e-4 is too loose. Needed 1e-8 or tighter.
- **Whether the experimentator's coordinate_descent.py is correct at N=30k.** Large-array
  tests were not completed.

## 3. What given facts might be wrong or outdated?

- **fact_002** (target C ≤ 1.5053): Already beaten since gen 3. Should be updated or noted
  as historical only.
- **pattern_013** ("~6500 near-max points"): explore_2 showed tight@1e-4 = 18325 and
  tight@1e-5 = 16185 at N=30k. The pattern should specify epsilon level. The commonly
  cited "6500" is tight@1e-7.
- **State of Affairs' coverage map**: Listed "LP at N=5000-10000: plateau size unknown" —
  now partially answered by explore_2 (downsampling produces C=7+, not answerable this way).

## 4. Was the State of Affairs accurate?

Largely yes. The frontier identification (triplet perturbation on TTT-Discover 30k) was
correct. The prioritized untested combinations (interleaved cycles, quadruplets, momentum
triplets, LP at intermediate N) were all addressed this generation.

**One gap:** The State of Affairs didn't warn that downsampling from N=30k would produce
terrible solutions (C=3-7). The assumption was that interpolation would preserve C near 1.503.

**One missing context:** The State of Affairs noted triplet follow-up "found 0 in 20k
additional trials" but didn't clearly signal that this means triplet space is nearly exhausted.
exploit_2's momentum triplet attempt was reasonable per the State of Affairs but was
essentially re-confirming exhaustion.

## 5. What would I do differently with more or different context?

- I would have flagged the momentum triplet experiment as low-priority given the second-pass
  zero-improvement result already documented. The quadruplet experiment was correctly
  prioritized as highest-value.
- I would add effective safe-set margins to pattern_012 or create a fact about autoconv
  plateau geometry (tight constraint counts at various epsilon levels).

## 6. Specific experiments to run

### Experiment A: Full interleaved multi-order cycle (HIGHEST PRIORITY)
**Protocol:** Starting from gen 8 explore_1's best array (C=1.5028628685):
1. Coord descent (full-array, 3 rounds or until <10 improvements per round)
2. Triplet perturbation (30k trials, all 4 strategies)
3. Quadruplet perturbation (30k trials, drop S2)
4. Repeat from step 1
5. Stop when all 3 methods find 0 improvements in the same cycle
**Expected:** 2-4 cycles before full convergence. Total improvement O(1e-10).

### Experiment B: Quintuplet perturbation
**Protocol:** d1+d2+d3+d4+d5=0 with 4D gradient projection. Same implementation
pattern as quadruplets. 50k trials.
**Expected:** If quadruplets find improvements where triplets can't, quintuples
may find improvements where quadruplets can't.

### Experiment C: Vectorized batch trial evaluation
**Protocol:** Sample K=100 quadruplets simultaneously. Compute all gradient
directions as a matrix op. Evaluate all step sizes via broadcasting. Accept
first improving candidate.
**Expected:** 10-50x throughput improvement (1000+ trials/s vs 112).

### Experiment D: Near-optimal N=5000 from scratch
**Protocol:** Initialize N=5000 array, run Adam + smooth-max to reach C~1.509 basin,
then coord descent to convergence. Measure tight constraint counts at various epsilon
levels. If tight@1e-5 < 500, attempt LP refinement.
**Expected:** 30-60 min compute. May finally answer the LP tractability question.

## 7. What surprised me?

1. **8015 quadruplet improvements.** Gen 7 triplets found 160. The ~50x increase in accepted
   moves suggests the landscape has rich higher-dimensional structure that lower-order
   methods can't access. However, the total C improvement is similar magnitude (~4e-10 for
   quadruplets vs ~3.6e-9 for triplets) — the per-move improvement is smaller.

2. **2523 triplet follow-up improvements after quadruplets.** This is the strongest evidence
   yet for the unlocking hypothesis. Gen 7's second triplet pass found 0 in 20k trials, but
   after quadruplet modification, triplets find 2523 improvements. The landscape reshaping
   is not subtle.

3. **2008 coord descent improvements after triplets (exploit_1).** Gen 7 exploit_1 had
   converged coord descent to 16 improvements in round 6. But after gen 7 explore_1's 160
   triplet perturbations, 2008 new coord descent directions opened up. This is the clearest
   proof of interleaving value.

4. **Momentum triplets: complete zero.** Not even Strategy 1's mass redistribution approach
   with amplification and neighbor chains found a single improvement. The triplet landscape
   on the unmodified gen 7 best is truly exhausted for this strategy.

5. **FFT padding: perfectly identical.** Differences were <1e-15 across all padding sizes.
   I expected at least 1e-12 rounding differences. The computation is numerically stable.

## 8. Helper tools feedback

Not directly applicable (I'm the evaluator, not a solution agent). However, based on agent
reports:

**Working well:**
- `incremental_autoconv_update.py`: Core enabling technology for all perturbation methods.
  Correct, essential, O(N).
- `compute_c_f64.py`: Correct, used for verification by all agents.
- `cross_convolution_f64.py`: Correct, used for initialization.

**Issues reported by agents:**
- `incremental_update` allocates a new array on each call. For high-throughput trials (coord
  descent with 48 deltas × 30k elements), allocation overhead dominates. An in-place or
  trial-only variant would help.
- `lp_matrix.py` (`scipy_lp_solve`): Misleading docstring about t<0 being the improvement
  indicator — t is actually constrained ≥0 by construction.
- `helpers/README.md` still lists "none yet" for experimentator-created helpers despite 7-8
  deployed helpers. Needs update.

**Missing helpers (agent requests):**
- Vectorized batch trial evaluator (K candidate index-sets evaluated simultaneously)
- `triplet_incremental_update`: Batch 3-element update in one O(N) pass
- `coordinate_descent_round` helper (partially built by experimentator_1, needs large-array validation)
- General k-plet perturbation module
