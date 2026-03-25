---
type: pattern
id: pattern_004
name: "Current optimization floor around C ~ 1.5168"
lifecycle: active
confidence: 0.7
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol11, gen001_explore_1_sol12]
related_ideas: [idea_004, idea_007]
tags: [performance-floor, frontier]
---

With the current approach (flat-block init -> multi-scale Adam -> basin hopping), the best
achievable score appears to be C ~ 1.5168. Both basin hopping solutions (5 rounds and 10
rounds) converged to nearly identical scores, suggesting this is a hard floor for this
approach family.

The gap to target (1.5053) is 0.0115. The gap to the known best upper bound (1.5098) is
0.0070. Closing this gap likely requires a qualitatively different approach — either:
1. Multi-bump initializations that access a different basin (idea_011)
2. Symmetry enforcement + bimodal init (idea_009 + idea_011)
3. Softplus reparameterization changing the loss landscape (idea_010)

Incremental improvements to Adam + multi-scale are unlikely to break this floor.
