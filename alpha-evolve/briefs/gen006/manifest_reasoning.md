# Manifest Reasoning — Generation 6

## Situation Assessment

**Score trajectory:** 1.5091 → 1.5032 → 1.5029 → 1.5029. Gen 5 achieved the first agent-driven improvement (delta = -8.82e-9 via float64 coordinate descent), but gen 5 overall showed no improvement in best score after rounding. The pipeline is at a micro-optimization frontier where improvements are at float64 precision limits.

**Key discoveries from gen 5:**
1. Float32/float64 precision mismatch corrupts all optimization decisions below C~1.505 (pattern_008)
2. Gradient-based methods (smooth-max Adam, projected gradient, normalized gradient) are ALL exhausted on the TTT-Discover 30k array
3. Float64 coordinate descent found 116 micro-improvements but hit diminishing returns quickly
4. SA at coarse scale definitively closed regardless of calibration (pattern_009)
5. Five intermediate AlphaEvolve arrays extracted (N=600 to N=5000)

**Critical infrastructure gap:** The compute_c_f64 helper has been requested by 4 agents across 2 generations and recommended by the System Critic 3 consecutive times. Every exploit agent wastes 30+ minutes reimplementing it. This is now MANDATORY per architect rules.

**State of Affairs staleness:** The SoA is from gen 3 — 3 generations out of date. The consistency review was requested 3 times. The orchestrator should run it before gen 7 at the latest. Gen 6 briefs manually override all stale SoA guidance.

## Agent Mix Rationale (5 agents)

### experimentator_1 (opus, 1200s) — compute_c_f64 helper
**Why:** MANDATORY. The compute_c_f64 helper has appeared in system_recommendations for 3 consecutive generations (gen 3, 4, 5) unresolved. Per architect rules: "you MUST include an experimentator instance to build it." This helper will save ~30 minutes per exploit agent in all future generations. Also updates sensitivity.py with float64 mode and fixes the stale README.

**Why opus:** Helper creation requires precise matching of validate.py's float64 arithmetic and careful API design. Precision matters more than speed here.

### exploit_1 (opus, 1500s) — Extended float64 coordinate descent
**Why:** Direct continuation of gen 5's only success (exploit_2's 116 improvements). Gen 5 only scanned top-500 elements in 10 passes. Extending to top-2000 elements, 30 passes, and finer deltas is the lowest-risk path to improvement. Also includes bulk LP residual cleanup (zeroing all near-zero elements simultaneously). Additionally, this agent will produce a properly baked solution — replacing the 792s eval-time best.py.

**Why opus:** Micro-optimization requires meticulous float64 precision work. The improvement target is 1e-8 scale. This is the highest-value exploit slot.

**Timeout:** 1500s based on gen 5 exploit_1 (1501s work + 143s wrap-up = 1644s) and exploit_2 (1501s + 228s = 1730s). Both timed out at 1500s but produced useful work in wrap-up.

### exploit_2 (sonnet, 1200s) — Pattern_007 float64 re-test
**Why:** Pattern_007 ("published solutions are local minima for smooth-max Adam") governs the entire pipeline strategy. It closed warm-start optimization. ALL evidence was collected with float32 accept/reject decisions. Gen 5 proved float32 is unreliable at this precision level. If float64 re-test shows Pattern_007 is wrong, the pipeline regains an entire optimization strategy. This is a high-value binary test: either confirms or overturns the most influential conclusion in the knowledge base.

**Why sonnet:** The protocol is well-defined (run smooth-max Adam on N=600 array with float64 tracking). Execution, not invention.

**Target array:** research_1/sol02 (N=600, C=1.5040) — same resolution as our pipeline, no interpolation needed, lower starting C than sol01.

### full_1 (opus, 1500s) — LP-based constraint relaxation
**Why:** LP is the ONLY method that has ever produced sub-1.505 scores. Both AlphaEvolve and TTT-Discover used LP-based approaches. Five agent reports across 2 generations identified LP as the only viable path forward. This has never been attempted in our pipeline despite being the highest-priority recommendation since gen 4. The implementation is engineering-intensive (linearized LP formulation, near-tight constraint identification, iterative application) — that's why it gets a full agent with opus.

**Why opus:** LP formulation requires mathematical precision. The linearization of the quadratic autoconvolution constraint is non-trivial. A wrong formulation wastes the entire session.

**Timeout:** 1500s — this is complex engineering work. Gen 5 full_1 took 1005s (900s + wrap-up). LP is harder than what full_1 did in gen 5.

### explore_1 (sonnet, 1200s) — Warm-start N=600 arrays with float64
**Why:** The N=600 AlphaEvolve arrays (C=1.5040, C=1.5053) are LP-optimized at our pipeline's native resolution. They've never been warm-started. If smooth-max Adam can improve them (especially with float64 accept/reject), it opens an entire class of experiments. If it can't, it provides additional evidence for or against Pattern_007. Also tries float64 coordinate descent on N=600 as a fallback — these smaller arrays may have more room for element-wise improvement than the 30k array.

**Why sonnet:** The protocol follows established patterns (warm-start + Adam + tracking). Cost efficiency.

## What I chose NOT to do

1. **Research agent:** No research agent this gen. All published arrays have been extracted (gen 5 research_1). The remaining research questions (structural analysis, Cell 91 identity) are lower priority than active optimization attempts. If LP refinement (full_1) needs structural analysis, the agent can do it as part of its work.

2. **Genetic crossover:** No genetic agent. The population has two solution families (gradient-descent at ~1.509 and LP-optimized at ~1.503). Crossing them is unlikely to produce anything useful — the LP solutions dominate in every dimension.

3. **Additional explore agents:** One explore is sufficient. The coverage matrix shows the explore space for gradient-from-random-init is exhausted (cluster_002 marked stale). The only explore value is warm-start experiments.

4. **visualize.py helper:** Requested since gen 3 but consistently lower priority than compute_c_f64 and optimization work. Deferred again.

## Timeout Calibration

| Agent | Timeout | Rationale |
|-------|---------|-----------|
| experimentator_1 | 1200s | Gen 5 experimentator took 2166s total (1200+900+966). 1200s work should be sufficient for 3 helper files + validation. |
| exploit_1 | 1500s | Gen 5 exploits used 1500s work time. Coordinate descent at N=30000 is compute-heavy. |
| exploit_2 | 1200s | Smooth-max Adam at N=600 is fast (~0.5ms/step). 1200s is generous for 2 seeds × 90k steps. |
| full_1 | 1500s | LP formulation + iterative application is engineering-intensive. Match exploit timeout. |
| explore_1 | 1200s | Warm-start protocol is well-defined. Same as exploit_2. |

## Risk Assessment

1. **All 5 agents need float64 compute_c** but the experimentator's helper won't be available until gen 7. Each agent must implement its own. This is wasteful but unavoidable given parallel execution.

2. **LP formulation may be incorrect.** The linearization of the quadratic constraint is the key technical risk. If full_1 gets the math wrong, the entire LP session is wasted. Mitigated by assigning opus.

3. **Pattern_007 re-test may be inconclusive.** If warm-start improves C by 1e-7 (float64 noise level), it's unclear whether Pattern_007 is truly wrong or the improvement is numerical artifact. The brief instructs exploit_2 to report magnitude clearly.

4. **exploit_1 may find no additional improvements** beyond gen 5 exploit_2's 116. Coordinate descent diminishing returns were already visible (72/116 in pass 1). The top-2000 extension is speculative.
