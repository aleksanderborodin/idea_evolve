---
type: idea
id: idea_016
name: "LP-guided memetic algorithm (AlphaEvolve approach)"
lifecycle: active
confidence: 0.7
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen003_research_1_sol01]
contradicted_by: []
related_ideas: [idea_014, idea_001, idea_006]
cluster: cluster_003
tags: [LP, memetic, alphaevolve, hybrid, simulated-annealing]
---

AlphaEvolve's actual algorithm is a hybrid memetic approach combining:
1. LP-guided gradient direction (solve_convolution_lp for descent directions)
2. Cubic backtracking line search with momentum
3. Simulated annealing perturbations with sine-map pseudo-random generator
4. Temperature cooling tied to remaining runtime

This is NOT coarse-grid SA (that was Boyer et al., a different paper). The
AlphaEvolve method works at the full resolution and uses LP to find descent
directions that the standard gradient may miss.

**Evidence:** The 1319-element solution (C=1.5032) has qualitatively different
structure from our gradient-descent solutions: dense non-zero region in first
~25 elements, large sparse gap (near-zero for ~100 elements), then complex
multi-peaked structure with many near-zero valleys. This suggests the LP-guided
approach navigates a fundamentally different part of the solution space than
Adam + smooth-max.

**Implication:** Our pure gradient descent pipeline may be structurally limited
to the ~1.509 basin neighborhood. Reaching 1.503-level scores may require
either (a) warm-starting from published solutions (idea_014) or (b)
implementing elements of the LP-guided approach.

**Not yet implemented.** The LP component requires formulating and solving a
linear program at each step, which is a significant implementation effort.
