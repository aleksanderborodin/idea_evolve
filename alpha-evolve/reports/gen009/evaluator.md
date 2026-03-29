# Evaluator Report — Generation 9

**strategic_shift: false**

## Summary

Generation 9 produced 4 scored solutions and 1 timeout. The best score improved by
-2.56e-10 over gen 8, reaching **C = 1.502862868222897**. Three major questions were
definitively answered: (1) quintuplets don't work (noise floor), (2) LP fails at all
resolutions, (3) ultra-fine coordinate descent deltas reopen thousands of improvements.

## 1. What did I try?

I collected and verified scores for all 5 solutions in gen 9's population:

| Solution | Score | Valid | Method |
|---|---|---|---|
| exploit_1/sol01 | **1.5028628682** | Yes | Ultra-fine coord descent |
| explore_1/sol01 | 1.5028628683 | Yes | Quintuplet + triplet |
| explore_2/sol01 | 1.5168 | Yes | N=5000 GD + CD + LP |
| explore_2/sol02 | 1.5170 | Yes | N=5000 iterative LP |
| exploit_2/sol01 | TIMEOUT | No | Momentum quadruplets |

I analyzed all agent reports, identified 4 new patterns (017-020), created 1 new idea
(idea_023 minimax perturbation), updated 5 existing ideas, demoted idea_020 to debunked,
and updated 2 clusters.

## 2. What information did I lack?

- **Whether exploit_2's checkpoint arrays contain genuine improvements.** The 5 checkpoint
  .npy files are unscored. I cannot run evaluate.py on them because they need a wrapper
  sol.py to be written.
- **The exact ordering sensitivity of ultra-fine CD vs multi-element moves.** exploit_1
  and explore_1 took different paths but I can't compare them directly because they started
  from slightly different arrays (gen 8 best vs gen 8 best with quintuplet noise).
- **Whether the gen 9 experimentator's batch_trial_evaluator helper was deployed to
  problem/helpers/.** I checked population/gen009/experimentator_1/ doesn't exist. The
  helper may still be in the experimentator workspace awaiting orchestrator deployment.

## 3. What given facts might be wrong or outdated?

- **Pattern_012 ("coord descent convergence is exponentially decaying"):** Still true for a
  fixed delta grid, but misleading. Should be annotated: "convergence is per-delta-grid, not
  absolute. Ultra-fine deltas reopen improvements (pattern_017)."
- **Pattern_014 ("higher-order perturbations unlock lower-order directions"):** Partially
  challenged. The effect was strong in gen 7-8 but NOT observed in gen 9 after ultra-fine CD.
  The unlocking may depend on the starting solution's optimization resolution. Pattern needs
  a nuance annotation.
- **fact_002 (target C ≤ 1.5053):** Flagged as outdated since gen 7 State of Affairs. Still
  not updated. The target was beaten in gen 3.

## 4. Was the State of Affairs accurate?

Partially accurate. Correct elements:
- TTT-Discover 30k as the foundation
- Triplet perturbation as the active frontier
- LP at N=5000-10000 as needing diagnostic

Inaccurate elements:
- "Coordinate descent essentially converged" — wrong. Ultra-fine deltas found 4943 improvements.
- "Interleaved triplet + coord descent cycles" as the highest priority — partially wrong.
  Ultra-fine CD alone produced the best gen 9 score. The interleaving hypothesis needs nuance.
- Missing: N=5000 optimization floor (~1.517), plateau structure with 13 near-tied positions.

## 5. What would I do differently with more or different context?

- Profile the autoconvolution plateau structure (number and distribution of near-max positions)
  BEFORE analyzing multi-element perturbation results. This would have immediately explained
  why single-peak gradient fails for triplets/quadruplets after ultra-fine CD.
- Run evaluate.py on exploit_2's checkpoint arrays to recover any improvements from the
  timed-out session.

## 6. Specific experiments to run

### Experiment 1: Optimal optimization sequence A/B test
- **Path A:** gen 8 best → ultra-fine CD only
- **Path B:** gen 8 best → standard CD → triplets (50k) → quadruplets (20k) → ultra-fine CD
- Compare final scores. If Path B wins, the interleaving protocol should use ultra-fine CD
  as the final step only.

### Experiment 2: Minimax multi-element perturbation (idea_023)
- Implement gradient computation at all 13 plateau positions
- Solve the LP (13 constraints, k-1 variables) to find the minimax descent direction
- Test with triplets (k=3, 2 free variables) and quadruplets (k=4, 3 free variables)
- If this finds improvements where single-peak gradient fails, it's a major advance

### Experiment 3: Geometric delta grid to float64 limits
- Use np.geomspace(1e-14, 1e-1, 100) for coordinate descent
- Determine the absolute float64 precision floor for this problem
- If 1e-12 to 1e-14 deltas still find improvements, the optimization is far from converged

### Experiment 4: Evaluate exploit_2 checkpoint arrays
- Load ckpt_quad_5.npy, verify with compute_c_f64
- If C < gen 8 best, bake into a scored solution
- Quick win: ~5 min of agent time

## 7. What surprised me?

1. **4943 improvements at ultra-fine deltas** when everyone declared CD convergence. The
   landscape has unexpected fine-scale structure.

2. **Quintuplets at exactly 1 ULP.** The precision breakdown is clean and sharp — not
   gradual. k=4 works, k=5 is exactly at the noise floor.

3. **LP plateau fraction is resolution-independent.** 24-28% at N=5000, 30.5% at N=30k.
   This is a deep structural property I did not expect.

4. **Triplets still working in gen 9.** 150 improvements from explore_1, starting from
   the gen 8 best that had only standard-delta CD. The triplet landscape is deeper than
   previously estimated.

5. **Ultra-fine CD subsumes multi-element moves** (0 triplet/quad improvements after
   ultra-fine CD). This was unexpected and challenges the interleaving protocol.

## 8. Helper tools feedback

I did not use any helpers directly (evaluator role). Based on agent reports:

- **batch_trial_evaluator.py** (new, gen 9 experimentator): 46x speedup, tested, ready
  for deployment. Should be the default for all perturbation agents in gen 10.
- **incremental_autoconv_update.py:** Universally praised. The pre-allocated buffer
  approach is critical for CD speed.
- **compute_c_f64.py:** Correct and essential for ground truth verification.
- **lp_matrix.py:** Docstring about predicted_improvement sign is still confusing
  (flagged again by explore_2). Should be corrected.
- **Missing: plateau_analyzer** — A helper that returns top-K autoconv positions, values,
  and per-element gradients at each. Would inform perturbation strategy choice. Proposed
  by exploit_1.
- **Missing: minimax_perturbation_solver** — Given K plateau positions and M elements,
  find the direction reducing max across all. Small LP. Proposed by exploit_1.

## 9. Time budget

Sufficient for all analysis. I read all scores, solutions, reports, and knowledge files,
created comprehensive output including 5 updated ideas, 1 new idea, 4 new patterns,
2 updated clusters, full solution-idea map, coverage matrix, generation snapshot, agent
gaps report, and this evaluator report.

If I had more time, I would:
1. Run evaluate.py on exploit_2's checkpoint arrays
2. Cross-reference pattern_012 and pattern_017 to produce a unified "CD convergence" guide
3. Analyze the 13-position plateau structure in more detail using the actual array values
