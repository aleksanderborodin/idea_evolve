---
type: idea
id: idea_022
name: "Bose-Chowla Affine Plane Construction"
lifecycle: established
confidence: 0.95
first_seen: generation_5
last_updated: generation_6
last_confirmed_gen: 6
supported_by: [gen005_experimentator_1_sol01, gen005_research_1_sol01, gen006_exploit_1_sol01, gen006_full_1_sol01]
contradicted_by: []
related_ideas: [idea_006, idea_004, idea_011, idea_020]
cluster: cluster_001
tags: [algebraic, bose-chowla, affine-plane, construction, high-impact]
---

The Bose-Chowla affine plane construction (type "ap" in Rokicki-Dogon) generates Sidon
sets of size q for prime q, using a different algebraic structure than Singer (projective
plane, size q+1). For prime q, the construction operates in Z_{q^2-1} and applies a
multiplier to optimize span.

**Generation 5 — BREAKTHROUGH**:
- **q=107, multiplier=433**: 105-mark ruler with span=9884. All 105 elements fit in
  {0, ..., 10000}. **Fitness = 105** (pipeline best, +3 over Singer q=101).
- Two independent implementations confirmed (experimentator_1, research_1).

**Generation 6 — STRUCTURAL ANALYSIS**:
- **Self-healing property** (pattern_014): Removing any k elements (k=1-104) opens exactly
  k addable slots = the removed elements. 27K+ perturbation trials, all return 105.
- The swap landscape around 105 is completely flat (zero extensible alternatives).
- Singer pp q=107/109/113 exhaustive multiplier search: max 105/104/102 in [0,10000].

**Algebraic ceiling**: 105 is the maximum achievable by any known algebraic construction for N=10000.

**Maximality**: The 105-mark set is greedy-maximal with zero combinatorial slack.

**Gen 6 consistency fix**: Added gen 6 solutions to supported_by. Added idea_011 to related_ideas.
