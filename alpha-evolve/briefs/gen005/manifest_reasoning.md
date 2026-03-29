# Manifest Reasoning — Generation 5

## Situation Assessment

**Score trajectory:** 1.5091 (gen2) → 1.5032 (gen3, -0.0059) → 1.5029 (gen4, -0.0003). Both improvements came from **retrieval** of published solutions (AlphaEvolve, TTT-Discover), not agent optimization. The gradient-descent pipeline remains stuck at C≈1.509. No agent has ever improved a published solution.

**Key gen 4 findings:**
- Pattern_007 confirmed: smooth-max Adam with softplus reparameterization CANNOT improve published solutions at any temperature or learning rate
- Root cause identified: softplus dead zones at near-zero elements freeze gradients
- TTT-Discover 30k array retrieved (C=1.50286), now the new best
- Calibrated SA at N=23 was correctly implemented but timed out (10× budget overrun)
- Three helpers (sensitivity_map, inv_softplus_safe, interpolate_sparse) are now deployed

**Critical question for gen 5:** Can any agent-driven optimization method improve a published solution? If not, we're limited to retrieval.

## Agent Mix Rationale (4 agents)

### exploit_1 (opus, 1500s) — Projected Gradient Descent on TTT-Discover 30k

**The #1 priority experiment.** Five agents across three generations have recommended projected gradient descent but it has never been implemented. This bypasses the confirmed failure mode (softplus dead zones) by optimizing f directly with non-negativity clamping. Uses the sensitivity_map helper.

Opus because: this requires precise implementation of a novel optimization approach on a large array. Getting the learning rate regime right (1e-7 warmup to 1e-5) is critical — too high destroys the solution (gen 4 lesson).

Timeout 1500s because: N=30000 steps may be slow (~10-40ms each). Need margin for timing benchmark + multiple variants.

### exploit_2 (opus, 1500s) — Sensitivity-Guided Coordinate Descent on TTT-Discover 30k

**Complementary to exploit_1.** Even simpler — perturb individual elements, keep improvements. Uses sensitivity_map to focus on the top-500 most sensitive elements. No parameterization issues, no gradient approximation. If coordinate descent finds even a tiny improvement, it proves the solution isn't at a strict element-wise local minimum.

Opus because: needs careful implementation to avoid wasting compute on insensitive elements. Must correctly handle the 30k-element array efficiently.

Timeout 1500s because: 15000 compute_c calls at ~10ms each ≈ 150s for the core loop, plus exploration of block perturbations. Generous margin for multiple passes.

### explore_1 (sonnet, 1200s) — Calibrated SA at N=23 (Reduced Budget)

**Third attempt, fixed budget.** Gen 3 had wrong calibration. Gen 4 had correct calibration but 10× too many iterations. This attempt: 2 seeds, 100 SA iters, 300 inner steps = ~30s of SA compute. Uses interpolate_sparse helper for N=23→N=600 upsample (not cubic spline). Includes timing benchmark and early stopping.

Sonnet because: the implementation is well-specified and straightforward. The brief contains exact parameter values.

Timeout 1200s because: gen 4 explore_1 used 1200s and timed out due to budget, not complexity. With 10× reduced budget, 1200s is generous.

### research_1 (sonnet, 900s) — Extract Intermediate Published Arrays

**Completes gen 4 research_1's unfinished work.** Cell 47 (N=600, C≈1.5053) is immediately usable by our gradient pipeline — no interpolation needed. Cell 50 (N=600, C≈1.5040) gives a second warm-start target. These enable a class of experiments that were impossible before.

Sonnet because: web retrieval and array extraction is routine work.

Timeout 900s because: gen 4 research_1 completed the hard part (finding the notebook, mapping cells) in 900s. Extraction is simpler.

## What I Deliberately Did NOT Do

1. **No experimentator.** The system recommendations said to create three helpers, but ALL THREE already exist (`inv_softplus_safe`, `sensitivity_map`, `interpolate_sparse`). The helpers README is stale but the files are deployed.

2. **No smooth-max warm-start experiments.** Pattern_007 is confirmed. Any smooth-max Adam warm-start of published solutions is a dead end. Period.

3. **No additional explore instances.** The coverage matrix shows all gradient-descent-from-random-init approaches converge to ~1.509. More explores in that space would be wasted compute. The one explore (SA at N=23) targets the only remaining untested coarse-search method.

4. **No genetic crossover.** The two best solutions (TTT-Discover 30k and AlphaEvolve 1319) have completely different structures and resolutions. Meaningful crossover requires solving the resolution mismatch, which is an unsolved problem.

5. **No ultra-conservative warm-start (Experiment 6 from suggestions).** This is lower priority than projected gradient and coordinate descent. If both exploit agents fail to improve the TTT-Discover array, ultra-conservative warm-start is unlikely to succeed either — it's a weaker version of the same idea.

## Risks

1. **N=30000 may be too large for efficient JAX optimization.** Both exploit agents depend on JAX working efficiently at N=30000. If step time exceeds ~50ms, the exploit agents won't have enough steps to converge. Mitigation: both briefs mandate a timing benchmark first.

2. **Coordinate descent may be O(N²) in practice.** 500 elements × 4 perturbation sizes × 10 passes × compute_c(30000) could be slow. Mitigation: compute budget is estimated at ~150s, well within timeout.

3. **SA at N=23 may simply reproduce the 1.509 attractor.** If the 1.509 basin is genuinely global for functions of this class (not just for smooth-max Adam), SA won't help. This would be a valuable negative result.

4. **Cell 47 array may not be extractable.** The AlphaEvolve notebook's exact URL and cell structure may have changed since gen 4. Mitigation: research_1 has the observations from gen 4 with exact cell numbers.
