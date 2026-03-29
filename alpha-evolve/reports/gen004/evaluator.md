# Evaluator Report — Generation 4

**strategic_shift: false**

## 1. What Did I Try?

I evaluated all 5 solutions from gen 4 (4 agents × 1-2 solutions each). Collected
verified scores from `.score` sidecar files for 4 solutions; confirmed that explore_1/sol01
lacks a `.score` file and exceeds evaluation timeout (the solution runs ~600k gradient
evaluations). Ran evaluate.py on explore_1/sol01 — confirmed timeout.

Analyzed each solution's strategy against the existing knowledge base. Identified
2 new ideas, 1 new pattern, and 4 updated ideas. Updated 2 clusters, the solution-idea
map (added 5 gen-4 entries), and the coverage matrix (added 4 new rows).

## 2. What Information Did I Lack?

- **TTT-Discover method details.** The paper title "Learning to Discover at Test Time"
  is not obviously about autocorrelation. Understanding the LP formulation and how the
  LLM guides it would help assess whether we can implement a simplified version.
- **Exact structure comparison between TTT-Discover 30k and AlphaEvolve 1319 arrays.**
  I read the first 30 lines of the 30k array but a full structural analysis (sparsity
  pattern, frequency content, mass distribution) would be valuable.
- **Wall-clock evaluation time for explore_1/sol01.** I know it exceeds the timeout
  but don't know by how much (5 min? 30 min?). This would help calibrate future SA budgets.

## 3. What Given Facts Might Be Wrong or Outdated?

- **"Cell 91 contains ThetaEvolve's 1.503133"** — CONFIRMED WRONG by research_1.
  Cell 92 is for the second autocorrelation inequality. ThetaEvolve = AlphaEvolve V2 = same
  1319-element array. This fact has been corrected in idea_014.
- **"Best known bound: C≤1.5029 by Yuksekgonul"** — NOW VERIFIED at C=1.50286.
  Slightly worse than advertised ≤1.5029 but close. The actual number should be used
  going forward.
- **State of Affairs says "warm-start smooth-max from 1.5032 array... may find
  improvements"** — WRONG. Confirmed in gen 4 that smooth-max Adam cannot improve
  this solution (pattern_007). State of Affairs needs updating.

## 4. Was the State of Affairs Accurate?

Mostly yes, with one critical inaccuracy:
- **Accurate:** Gradient-descent pipeline plateaued at ~1.509, published solutions are
  the only path forward, SA calibration was the key untested experiment.
- **Inaccurate:** The implicit assumption that smooth-max Adam could improve the 1.5032
  array. Three failed attempts in gen 4 prove this wrong. The State of Affairs should
  note: smooth-max Adam is a local minimum solver, not a basin escaper. Published
  solutions that were found by LP-based methods are already at their smooth-max floor.

## 5. What Would I Do Differently with More Context?

- Would have flagged the warm-start smooth-max approach as likely futile based on
  pattern_005 (1.509 basin depth) — if perturbation can't escape the 1.509 basin,
  smooth-max optimization from a deeper basin (1.503) certainly can't escape it either.
- Would have prioritized projected gradient descent and coordinate descent experiments
  as the only approaches with a chance of improving published solutions.

## 6. Specific Experiments to Run

**Priority 1 — Projected gradient descent on TTT-Discover 30k array:**
- Optimize f directly (not raw_params). After each Adam step, clamp f ≥ 0.
- Use very low lr (1e-6) and no temperature smoothing.
- This avoids the softplus dead-zone problem entirely.

**Priority 2 — Coordinate descent on 30k array:**
- For each index i in [0, 30000), try f[i] ± δ for δ in {0.001, 0.01}.
- Keep any change that lowers C. Repeat until convergence.
- Simple, gradient-free, no parameterization issues.

**Priority 3 — Sensitivity analysis of 30k array:**
- Compute ∂C/∂f[i] for all 30000 elements using JAX autodiff.
- Identify top-100 most sensitive elements.
- Focus optimization (coordinate descent or projected gradient) on those elements only.

**Priority 4 — Calibrated SA at N=23 with reduced budget:**
- 2 seeds, 100 SA iterations, 300 inner steps, 5k coarse steps, 10k fine steps.
- Same calibration protocol as explore_1 but ~10x less computation.

**Priority 5 — Retrieve intermediate published arrays at N=600:**
- Cell 46 (C=1.5053) and Cell 49-58 (C=1.5040-1.5033).
- These are at our gradient pipeline's resolution and may respond better to optimization.

## 7. What Surprised Me?

1. **The TTT-Discover result is not much better than AlphaEvolve despite 23× more
   elements (30k vs 1319).** Improvement is only 0.00030. This suggests the optimization
   landscape has very diminishing returns at this score level — each 0.0001 improvement
   requires qualitatively more effort.

2. **Smooth-max Adam completely fails to improve the 1.5032 solution.** I expected at
   least ~0.0001 improvement. Instead: literally zero improvement (3.8e-9 = noise).
   The AlphaEvolve solution is at a qualitatively different kind of local minimum than
   our gradient-descent solutions.

3. **T=0.005 immediately worsens the 1.5032 score to ~1.519.** The smooth-max
   approximation error at "normal" temperatures is huge for well-optimized solutions.
   This means our entire temperature annealing framework is inapplicable to warm-start
   optimization.

4. **Cell 92 being for the wrong problem.** Three generations of speculation about
   ThetaEvolve's array, resolved by research_1 actually looking at the data.

## 8. Helper Tools Feedback

- No helpers from `problem/helpers/` were used by any gen 4 agent.
- `helper.py` (`compute_c`) worked correctly for all agents.
- **Most wanted helper:** `inv_softplus_safe(array)` — inverse softplus with proper
  handling of near-zero values. Would save time for warm-start agents.
- **Second most wanted:** `sensitivity_map(f_array)` — compute ∂C/∂f[i] for all
  elements. Would enable targeted optimization experiments.
- **Third most wanted:** `interpolate_sparse(array, target_n)` — upsample preserving
  zero structure (piecewise-linear in non-zero regions, zero in zero regions).
