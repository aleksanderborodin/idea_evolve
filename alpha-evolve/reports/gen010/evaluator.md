# Evaluator Report — Generation 10

strategic_shift: false

## Executive Summary

Generation 10 produced 4 valid solutions, all improving on the previous best. The new overall best is C = 1.5028628681165177 (explore_2), improving by -1.064e-10. The generation definitively closed two open questions: (1) minimax LP perturbation (idea_023) is debunked — the solution is locally minimax-optimal for integral-preserving moves; (2) pattern_020 is confirmed — all multi-element integral-preserving approaches are fully subsumed by ultra-fine coordinate descent. Three major engineering discoveries (incremental drift, top-K screening, no convergence at 1e-13) provide clear guidance for gen 11.

## 1. What did I try?

### Score collection
Read .score files for all 4 solutions. All valid. No re-evaluation needed.

### Analysis
- Read all 4 solution source files (explore_2 and explore_1 run optimization during entrypoint, exploit_1 and exploit_2 bake arrays)
- Read all 6 reports (4 solution agents + experimentator_1 + architect)
- Read knowledge dump (ideas, clusters, patterns)
- Cross-referenced findings across agents for consistency

### Knowledge updates
- Updated 5 ideas (idea_019, idea_014, idea_021, idea_022, idea_023)
- Created 4 new patterns (pattern_021 through pattern_024)
- Updated pattern_020 to confirmed status
- Updated 2 clusters (cluster_001, cluster_003)
- Updated solution-idea map with all gen 10 entries
- Updated coverage matrix

## 2. What information did I lack?

- **Exact plateau position counts at the gen 10 best.** The knowledge dump says "13 within 1e-12" but explore_1 found K=28 within 1e-10 and K=15 within 1e-12. The actual count depends on the epsilon threshold and may shift with each CD round.
- **Detailed per-round improvement data from explore_2.** The report gives total (8003) but not per-round breakdown. Would help compare CD convergence rates across implementations.

## 3. What given facts might be wrong or outdated?

- **State of Affairs "Active protocol"** is now obsolete. It recommends "standard CD → triplets → quadruplets → ultra-fine CD." Gen 10 conclusively shows the correct protocol is ultra-fine CD only.
- **Pattern_012 (exponential decay)** needs clarification. The improvement COUNT does not decay (pattern_023). Only the real C improvement per round decays. These are different metrics.
- **batch_trial_evaluator "46x speedup"** is misleading for the current best solution (effectively 1x due to diffuse plateau).

## 4. Was the State of Affairs accurate?

**Accurate on:**
- Identifying ultra-fine CD as the dominant method (confirmed by all 4 agents)
- Identifying minimax as the highest-priority untested idea (tested and debunked)
- Warning about triplet ineffectiveness after ultra-fine CD (confirmed)

**Inaccurate/outdated:**
- "Active protocol" with multi-element interleaving — now confirmed obsolete
- No mention of incremental drift as a fundamental limitation
- batch_trial_evaluator speedup claim not applicable to current solution
- Missing the CD mechanism insight (integral adjustment vs peak reduction)

## 5. What would I do differently with more or different context?

- Would have flagged the CD mechanism distinction (integral-preserving vs non-integral-preserving) as a theoretical pattern earlier. It was latent in the data since gen 7 but never explicitly documented.
- Would have investigated whether the 4 agents' different final states represent genuinely different local minima or just different random walks through the same neighborhood.

## 6. Specific experiments to run

### Experiment 1: Per-round FFT resync CD (HIGHEST PRIORITY)
- Replicate exploit_1's approach but with resync every round (not every 5)
- Delta grid: np.geomspace(1e-14, 1e-1, 100)
- Top-K screening with K=30
- Expected: more reliable improvements, potentially reaching 1e-14 scale productively
- Time: 500s budget, ~7s/round, should achieve 70+ rounds

### Experiment 2: Multi-trajectory competition
- Run 5 independent CD trajectories (different seeds/element orderings) for 100s each
- Continue only the best trajectory for remaining 400s
- Different random orderings through the 30k-element space find different improvement paths
- exploit_1's baked solution was better than its dynamic run (different random trajectory)

### Experiment 3: Non-integral-preserving multi-element moves
- Allow d1+...+dk ≠ 0 (the integral can change)
- Optimize C = max_ac_new / integral_new² directly with k=2-3 free variables
- This is distinct from integral-preserving approaches (all exhausted)
- May find improvements invisible to single-element CD through coordinated moves that change both numerator and denominator

### Experiment 4: Starting from explore_2 best vs exploit_1 best
- Are these different local minima or same neighborhood?
- Run CD from explore_2's 1.5028628681165177 — does it find fewer/more improvements than starting from exploit_1's 1.5028628681839242?
- If they're different minima, crossover might help

## 7. What surprised me?

1. **All 4 agents improved.** In previous generations, typically 1-2 agents found improvements and 1-2 returned null or timeout. Gen 10 is the first generation where every solution agent beat the previous best. Ultra-fine CD is reliable and repeatable.

2. **Minimax LP universally returned t*≥0.** I expected at least some trials to find t*<0 (improving directions), even if they were too small to verify. The geometric inevitability (origin in convex hull with K=28) means no integral-preserving perturbation can help, period.

3. **exploit_1's 371k improvements in 71 rounds.** The sheer volume is staggering — and with no convergence trend. The 1e-13 landscape has effectively infinite fine-scale structure.

4. **Incremental drift is large.** 3.5x the real improvement after just 5 rounds. Prior generations' CD results may have been less reliable than reported.

5. **1e-14 improvements increasing.** As the solution is refined at 1e-13, new 1e-14 opportunities cascade. Suggests even finer structure exists below current exploration.

## 8. Helper tools feedback

- **plateau_analyzer.py** (new, experimentator_1): Built and validated this generation. Not used by optimization agents (arrived too late). Should be integrated into gen 11 briefs. Performance excellent (6.7ms).
- **incremental_autoconv_update.py**: Correct but needs drift warning in documentation.
- **batch_trial_evaluator.py**: Documentation misleading for current best solution. Needs caveat about diffuse plateaus.
- **compute_c_f64.py**: Essential for FFT resync verification. Correct.
- **Missing helper needed:** `topk_screened_cd()` — encodes exploit_1's top-K screening, drift management, and FFT resync in a reusable form. This would standardize the best CD approach for all agents.

## 9. Time budget

Sufficient for full evaluation. All output files written. No time pressure.

With more time, would have:
1. Verified the plateau position count at the new best (explore_2's) solution
2. Compared the 4 solutions' array structures to determine if they represent distinct local minima
3. Checked if any old experiments (gen006-gen008) need consolidation

## Experiment Consolidation

Checked `knowledge/experiments/` for results older than 3 generations:
- gen006, gen007, gen008 experiments exist. Key findings from these have already been incorporated into patterns (pattern_015: downsampling destroys structure, pattern_016: FFT padding validation) and facts. No further consolidation needed at this time.
- gen010/experimentator_1 results: plateau_analyzer helper validated. Will be deployed by orchestrator.

## Staleness Check

Ideas with `last_confirmed_gen` more than 5 generations old:
- idea_001 (gradient descent): last_confirmed gen 1. **STALE** (9 gens). However, irrelevant to frontier — gradient descent caps at C~1.509.
- idea_004 (coarse-to-fine): last_confirmed gen 5. **STALE** (5 gens). Same reason — irrelevant.
- idea_008 (multi-seed restart): last_confirmed gen 3. **STALE** (7 gens). Same reason.
- idea_012 (asymmetry): last_confirmed gen 3. **STALE** (7 gens). Established mathematical fact, no new evidence needed.

All stale ideas are either established mathematical facts or techniques from the superseded gradient-descent paradigm. No action needed — they are correctly documented as irrelevant to the current frontier.
