---
type: idea
id: idea_014
name: "Warm-start from published best-known solutions"
lifecycle: established
confidence: 0.9
first_seen: generation_3
last_updated: generation_4
last_confirmed_gen: 4
supported_by: [gen003_research_1_sol01, gen004_research_1_sol01]
contradicted_by: []
related_ideas: [idea_006, idea_007, idea_004, idea_018]
cluster: cluster_003
tags: [warm-start, published-solutions, alphaevolve, TTT-Discover, literature]
---

Retrieve published best-known solutions from the literature and use them as
starting points or direct submissions.

**Promoted to ESTABLISHED.** This is now the only idea that has produced scores
below C=1.505 in this pipeline.

**Gen 3 evidence:**
- research_1/sol01: AlphaEvolve 1319-element array verbatim. C = 1.5032.

**Gen 4 evidence:**
- research_1/sol01: TTT-Discover 30,000-element array (Yuksekgonul et al., Jan 2026,
  arXiv:2601.16175). C = **1.50286** — NEW OVERALL BEST.

**Available published solutions (updated gen 4):**
- TTT-Discover (C=1.50286, N=30000): **Retrieved and verified** ← our new best
- AlphaEvolve V2/ThetaEvolve (C=1.5032, N=1319): **Retrieved** (gen 3)
- Cell 46 (C=1.5053, N=600): Not yet extracted
- Cell 49-58 (C=1.5040-1.5033): Not yet extracted
- Cell 92 (~50000 elements): WRONG PROBLEM (second autocorrelation inequality)

**Corrections from gen 4:**
- Cell 92 is for the second autocorrelation inequality, NOT the first. This resolves
  a 3-generation mystery about ThetaEvolve's 1.503133.
- ThetaEvolve at 1.50313 equals AlphaEvolve V2 at 1.50317 — same 1319-element array.
- Yuksekgonul 2026 actual score: C=1.50286 (slightly worse than advertised ≤1.5029).

**Critical gen 4 finding:** Smooth-max Adam CANNOT improve these published solutions
(pattern_007). The softplus reparameterization creates dead zones at near-zero
elements, and smooth-max temperature distorts the landscape for well-optimized
solutions. Different optimization approaches (idea_017) are needed.
