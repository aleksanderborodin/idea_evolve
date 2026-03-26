# Evaluator Report — Generation 3

**strategic_shift: true**

## Executive Summary

Generation 3 produced a **strategic shift**. The research agent retrieved the AlphaEvolve published solution achieving C = 1.5032, beating our target of 1.5053 by 0.0021. Meanwhile, all gradient-descent-based approaches confirmed that the ~1.509 basin is inescapable via perturbation, SA, or extended annealing. The pipeline's focus must shift from "finding better basins via random init" to "polishing published solutions."

## 1. What Did I Try?

I evaluated all 10 solutions across 4 agents:

| Solution | Score | Valid | Key Finding |
|----------|-------|-------|-------------|
| research_1/sol01 | **1.5032** | 1 | AlphaEvolve array — TARGET BEATEN |
| explore_2/sol01 | 1.5090 | 1 | Arcsine init — marginal improvement |
| exploit_1/sol02 | 1.5091 | 1 | DCT perturbation — basin inescapable |
| explore_2/sol03 | 1.5091 | 1 | Arcsine 3-stage — no benefit from 3rd stage |
| explore_2/sol04 | 1.5092 | 1 | 25-seed funnel — arcsine dominates top-5 |
| exploit_1/sol01 | 1.5093 | 1 | Extended polish — 0.000025 improvement |
| explore_2/sol02 | 1.5102 | 1 | Arcsine sweep — high variance from noise keys |
| explore_1/sol01 | 1.5148 | 1 | Coarse SA N=40 — failed (metro_T too high) |
| explore_1/sol02 | 1.5155 | 1 | Coarse SA N=80 — failed (sigma uncontrolled) |
| explore_1/sol03 | 1.5169 | 1 | Coarse SA N=30 — failed (f values too large) |

Knowledge produced:
- 4 new ideas (idea_013-016): arcsine init, warm-start from published, DCT perturbation, LP-guided memetic
- 2 new patterns (pattern_005-006): basin depth, arcsine dominance
- 3 updated ideas: idea_004 (established), idea_007 (0.95 confidence), idea_010 (DEBUNKED)
- 1 new cluster (cluster_003): published solutions and warm-start
- Updated solution-idea map and coverage matrix

## 2. What Information Did I Lack?

- **The actual AlphaEvolve method details.** I relied on agent reports for algorithm description. A direct reading of the notebook code would have given more precise understanding of the LP-guided approach.
- **Whether the 50000-element Cell 91 array is ThetaEvolve's solution.** Unverified — could be a significant warm-start opportunity.
- **Yuksekgonul et al. (Jan 2026) solution details.** C <= 1.5029 reported but no public array found.

## 3. What Given Facts Might Be Wrong or Outdated?

- **"Boyer et al. coarse-SA-at-N=23" attributed to AlphaEvolve**: INCORRECT. research_1 clarified this is from a different paper. AlphaEvolve used LP-guided gradient + SA at full resolution. This misdirected explore_1's entire session. The State of Affairs must be corrected.
- **"AlphaEvolve used N=300 coarse grid"**: research_1 says the initial program used N=300, but the final evolved algorithm may have used different resolutions. Needs verification.
- **Best known bound was 1.5032**: Now 1.5029 (Yuksekgonul et al., Jan 2026).

## 4. Was the State of Affairs Accurate?

Mostly accurate, with one significant error:
- **CORRECT:** Smooth-max as most impactful technique. Coarse-to-fine with warm fine stage. Dead ends list. Coverage map.
- **INCORRECT:** The recommendation of "coarse-scale SA (Boyer et al. approach)" as the #1 priority experiment was based on incorrect attribution to AlphaEvolve. This sent explore_1 down a fruitless path.
- **MISSING:** Path to population/best.py (the AlphaEvolve solution was already there). The updated SOTA (1.5029). The qualitative structural difference between gradient-descent solutions and published solutions.

## 5. What Would I Do Differently?

- **Verify attributed methods before recommending.** The "Boyer et al. = AlphaEvolve" confusion wasted an entire agent's session.
- **Create a "warm-start priority" flag** in the State of Affairs when a solution significantly better than our best exists in the population.
- **Track raw_params alongside f-values** to enable warm-starting between generations.

## 6. Specific Experiments to Run

1. **HIGHEST PRIORITY — Warm-start from AlphaEvolve array (C=1.5032):**
   Load gen003_research_1_sol01.py, convert to raw_params via inv_softplus(f_values), run warm smooth-max Adam with tight schedule (T=0.005->0.002->0.0005->0.0001, 30k steps each). The 1319-element array may benefit from N=1319 smooth-max optimization that the original LP-guided algorithm didn't use.

2. **Warm-start from AlphaEvolve intermediate arrays:**
   Retrieve Cell 46 (C=1.5053, N=600) — this has the same resolution as our pipeline. Run full coarse-to-fine warm smooth-max. May bridge the gap between our 1.509 and the 1.5032 solution.

3. **Verify Cell 91 array** (~50000 elements): Extract and evaluate — if it's ThetaEvolve's C=1.503133, it's another warm-start opportunity.

4. **Coarse-scale SA with proper calibration:** If retried, mandate: (a) 5-iteration calibration phase first, (b) tune metro_temp for 20-40% acceptance, (c) use COLD inner optimizer (T=0.001 only, 3k steps) to avoid re-annealing back to same basin, (d) sigma = 0.05*mean(f) not 0.3.

5. **Arcsine reliability test:** Fix arcsine config (a=-0.05, b=0.22) and run 50 seeds to measure C distribution. Determine if 1.5090 is a better basin or noise.

## 7. What Surprised Me?

1. **The research agent produced the most impactful result of all 3 generations** — a single array retrieval beat the target, outperforming hundreds of gradient descent runs. This highlights the value of literature retrieval over pure optimization.

2. **The AlphaEvolve function structure is radically different from our gradient solutions.** Dense initial region, sparse gap, complex multi-peaked — not at all like the smooth bumps our optimizer produces. This suggests our gradient pipeline is trapped in a fundamentally different region of function space.

3. **Coarse-scale SA failed comprehensively.** All 3 agents (gen 2 + gen 3) recommended it as the #1 priority, yet it produced the worst scores in gen 3. The implementation had calibration issues, but the failure still raises questions about whether SA at any coarse scale can beat simple multi-seed restart.

4. **The 1.509 basin is deeper than anyone expected.** DCT perturbations up to 18% magnitude return to the same basin floor. This is not a normal local minimum — it's a massive attractor that captures almost all gradient-descent trajectories.

5. **The "Boyer et al. = AlphaEvolve" attribution error** persisted through 2 generations of briefs and State of Affairs without being caught. This underscores the importance of the research agent for fact-checking, not just retrieval.

## Staleness Check

All ideas have `last_confirmed_gen` within the last 3 generations. No staleness flags needed yet.

## Experiment Consolidation

No experiments older than 3 generations to consolidate (pipeline is only at gen 3).
