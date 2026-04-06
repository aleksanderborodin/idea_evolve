---
type: pattern
id: pattern_007
name: "ET(71) + local search plateaus at 75"
lifecycle: active
confidence: 0.8
first_seen: generation_2
last_updated: generation_2
evidence: [gen002_explore_1_sol03, gen002_explore_1_sol04]
related_ideas: [idea_009, idea_011]
tags: [erdos-turan, local-optimum, non-singer]
---

The Erdos-Turan construction for p=71, extended greedily and refined with 1-opt local search,
converges to exactly 75 elements. This is a robust local optimum: 25 independent random
restarts with different orderings all converged to 75.

This establishes a hierarchy of construction ceilings:
- Raw greedy: 66 (strict 1-opt local optimum, pattern_001)
- SA from greedy: 68
- ET(71) + greedy + 1-opt: 75
- Singer q=97: 98
- Singer q=97 + perturbation: 99 (pattern_004)
- Singer q=101 truncation: 102 (pattern_005)

The 27-element gap between ET-based approaches (75) and Singer (102) confirms that
algebraic construction quality is the dominant factor, not search refinement.
