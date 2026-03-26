---
type: idea
id: idea_016
name: "LP-guided memetic algorithm (AlphaEvolve approach)"
lifecycle: active
confidence: 0.75
first_seen: generation_3
last_updated: generation_4
last_confirmed_gen: 4
supported_by: [gen003_research_1_sol01, gen004_research_1_sol01]
contradicted_by: []
related_ideas: [idea_014, idea_001, idea_006, idea_018]
cluster: cluster_003
tags: [LP, memetic, alphaevolve, hybrid, simulated-annealing, TTT-Discover]
---

LP-guided optimization methods are the only approaches that have produced scores
below C=1.505 for this problem. Two independent implementations exist:

1. **AlphaEvolve** (Georgiev et al., Dec 2025): LP-guided gradient + SA memetic
   algorithm. Produced 1319-element array at C=1.5032.

2. **TTT-Discover** (Yuksekgonul et al., Jan 2026): LLM-guided LP with heuristic
   focusing on near-tight constraints. Produced 30,000-element array at C=1.50286.

Both use LP to find descent directions that standard gradients miss. The LP
formulation exploits the structure of the autoconvolution constraint to identify
which elements of the function to adjust and by how much.

**Gen 4 update:** The TTT-Discover method's success at N=30000 (vs AlphaEvolve's
N=1319) suggests that resolution matters for LP-based approaches — more elements
give finer control over the autoconvolution constraint.

**Not yet implemented in our pipeline.** Implementing even a simplified LP step
would be a significant engineering effort, requiring:
1. Formulating the autoconvolution constraint as a linear program
2. Solving the LP at each iteration to find descent directions
3. Combining LP directions with gradient descent

This remains the most promising path to beating C=1.5029 but is beyond the scope
of simple gradient-descent agents.
