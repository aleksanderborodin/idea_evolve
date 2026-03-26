---
type: idea
id: idea_014
name: "Warm-start from published best-known solutions"
lifecycle: active
confidence: 0.8
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen003_research_1_sol01]
contradicted_by: []
related_ideas: [idea_006, idea_007, idea_004]
cluster: cluster_003
tags: [warm-start, published-solutions, alphaevolve, literature]
---

Retrieve published best-known solutions from the literature and use them as
starting points for further optimization. The AlphaEvolve team (Georgiev et al.,
Dec 2025) published a 1319-element array achieving C = 1.5032 in the
`alphaevolve_repository_of_problems` GitHub repository.

**Gen 3 evidence:**
- research_1/sol01: Retrieved the AlphaEvolve array verbatim. C = **1.5032** —
  NEW BEST, beats the target of 1.5053 by 0.0021.

**Available published solutions (not all retrieved yet):**
- Cell 46 (C=1.5053, N=600): Original AlphaEvolve result
- Cell 49 (C=1.5040, N~1136): Intermediate improvement
- Cell 52-56 (C=1.5036-1.5035): Further intermediates
- Cell 58 (C=1.5033, N~3530): Near-best
- Cell 60 (C=1.5032, N=1319): Best retrieved ← our sol01
- Yuksekgonul et al. (Jan 2026): C <= 1.5029 — NOT YET PUBLIC in a repo
- ThetaEvolve (C=1.503133): Possibly in Cell 91 (~50000 elements), unverified

**Critical next step:** Warm-start gradient descent (smooth-max annealing) from
the 1.5032 array. The function has qualitatively different structure from our
gradient-descent solutions: dense region at start (~25 elements), sparse gap,
then complex multi-peaked structure with near-zero valleys. Our optimizer may
find further improvements from this starting point that it cannot reach from
random initialization.

**Important correction:** The "Boyer et al. coarse-SA-at-N=23" previously
attributed to AlphaEvolve is actually from a different paper. AlphaEvolve used
LP-guided gradient + SA memetic algorithm, not coarse-grid SA.
