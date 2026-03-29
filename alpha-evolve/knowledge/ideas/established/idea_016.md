---
type: idea
id: idea_016
name: "LP-guided memetic algorithm (AlphaEvolve approach)"
lifecycle: established
confidence: 0.8
first_seen: generation_3
last_updated: generation_10
last_confirmed_gen: 6
supported_by: [gen003_research_1_sol01, gen004_research_1_sol01, gen005_research_1_sol01, gen005_research_1_sol02, gen005_research_1_sol03, gen005_research_1_sol04, gen005_research_1_sol05]
contradicted_by: []
related_ideas: [idea_014, idea_001, idea_006, idea_018]
cluster: cluster_003
tags: [LP, memetic, alphaevolve, hybrid, simulated-annealing, TTT-Discover, established]
---

LP-guided optimization methods are the only approaches that have produced scores
below C=1.505 for this problem. Two independent implementations exist:

1. **AlphaEvolve** (Georgiev et al., Dec 2025): LP-guided gradient + SA memetic
   algorithm. Produced arrays from N=600 (C=1.5053) to N=5000 (C=1.5032).

2. **TTT-Discover** (Yuksekgonul et al., Jan 2026): LLM-guided LP with heuristic
   focusing on near-tight constraints. Produced 30,000-element array at C=1.50286.

**PROMOTED TO ESTABLISHED (gen 6 consistency review):**
- 7 supporting solutions across 3 generations, 0 contradictions.
- Two independent research groups validated LP-based approaches.
- Gen 5 exploit_1 exhausted ALL gradient-based approaches on the TTT-Discover 30k
  array — confirming LP solutions are strict local minima for gradient methods.
- Gen 6 exploit_2 confirmed with float64 rigor that smooth-max Adam cannot improve
  LP-produced solutions (pattern_007, confirmed).
- Higher resolution consistently helps LP methods (N=600->5000 for AlphaEvolve),
  unlike gradient descent where N>600 is counterproductive.

**Not yet implemented in our pipeline.** The only pipeline-side improvement of LP
solutions comes from coordinate descent (idea_019). Note: idea_020 (LP refinement
of existing solutions) was debunked — LP fails due to plateau structure (24-32%
near-maximal points at any N near optimality). Implementing a full LP-guided memetic
algorithm from scratch would be a major engineering effort distinct from idea_020.
