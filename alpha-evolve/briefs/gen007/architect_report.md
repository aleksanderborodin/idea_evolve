# Architect Report — Generation 7

## Data Anomalies

1. **helpers/README.md still says "none yet."** Four experimentator-created helpers are deployed in `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/` (compute_c_f64, sensitivity, inv_softplus, interpolation) but README was never updated. experimentator_1 is tasked with fixing this. Until then, agents reading only the README will think no helpers exist beyond core.py.

2. **Score progression shows 3-generation "stall" at 4-decimal display.** Gens 4-6 all show 1.502863 but actual improvements are -3.01e-4 (gen 4), -8.82e-9 (gen 5), -2.58e-8 (gen 6). The 4-decimal display hides real progress. System critic recommendation to extend precision display remains unaddressed — this is an orchestrator/dashboard change, not something agents can fix.

3. **pattern_007 duplicate files.** `active/pattern_007.md` (gen 4, confidence 0.85) still exists alongside `confirmed/pattern_007_update.md` (gen 6, confidence 0.95). The consistency review flagged this in gen 6 but the old file wasn't removed. No agents in gen 7 use smooth-max Adam, so this is cosmetic.

4. **fact_002 is outdated.** States "best known bounds 1.28 ≤ C ≤ 1.5098, target C ≤ 1.5053." Current best is C = 1.50286, target beaten since gen 3. Low impact — agents read the SoA (now updated) not individual facts for the current best.

5. **explore_1 session interruption in gen 6 was never diagnosed.** The agent produced zero output — no code, no solutions. Timing data shows 1200s work + 89s wrap + 36s debrief. The work phase consumed the full timeout (1200s) without producing anything. Possible cause: excessive file reading before coding. Gen 7 explore_1 brief explicitly says "Begin coding immediately. Do NOT spend more than 3 turns reading files."

## Confidence: Medium-High

**Why Medium-High (not High):**
- exploit_1 is high-probability (1800 improvements/round at round 3), but we don't know the convergence shape. Could drop sharply after round 5.
- LP at N=2000 is the highest-value experiment but also the highest-risk. The pseudocode in the brief is detailed but the linearization may have subtle errors.

**Why not Medium:**
- The consistency review ran in gen 6 — SoA is now fresh and accurate. No more stale guidance pollution.
- All helpers are deployed. No more agents reimplementing compute_c_f64 from scratch.
- Every brief is concrete with pseudocode. No vague directives.
- The gen 6 reports provided excellent methodology documentation for exploit_1 and full_1 to build on.

## What Didn't Fit

1. **Column generation LP strategy.** The experiment suggestions include starting with 10 variables and iteratively adding profitable columns. This is more sophisticated than the N=2000 downsampled approach and could handle full N=30000. Deferred to gen 8 — first prove LP works at any scale.

2. **CMA-ES in DCT subspace.** Listed in cluster_001 remaining opportunities. Speculative — no evidence it would outperform coordinate descent at the current frontier. Deferred.

3. **Batched gradient computation.** experimentator_1 in gen 6 noted that computing dC/df[i] for all i might be faster than N separate perturbations. This would accelerate coordinate descent further. Deferred to gen 8 experimentator.

## Strategic Risks

1. **All eggs in the TTT-Discover basket.** 4 of 5 agents work on or derive from the TTT-Discover 30k array. If there's a fundamental limit to coordinate descent on this array, gen 7 is a near-wipeout. exploit_2 on N=600 arrays is the only hedge.

2. **LP pseudocode may contain errors.** The linearization `delta_autoconv[j] ≈ 2*(f★delta_f)[j]` is a first-order approximation. For large delta_f, the quadratic term matters. The brief instructs conservative step sizes (alpha starting at 0.001) but the formulation could still produce wrong descent directions.

3. **Incremental autoconv update has no deployed helper.** exploit_1 must implement it from scratch (again). experimentator_1 will package it for gen 8, but gen 7 exploit_1 pays the reimplementation cost (~20-30 minutes).

## Open Questions for the System Critic

1. **Is the 4-decimal score_progression.md display causing strategic confusion?** Multiple agents and architects have flagged it. Is this an orchestrator config change or does it require code modification?

2. **Should we consider evaluating solutions at multiple FFT padding sizes as standard?** If exploit_1's padding validation shows padding-dependent scores, the evaluation pipeline itself may need updating.

3. **How should we handle the N mismatch between solution families?** TTT-Discover is at N=30000, AlphaEvolve ranges from N=600 to N=5000. Genetic crossover between families requires interpolation, which destroys sparse structure. Is there a resolution-invariant comparison method?
