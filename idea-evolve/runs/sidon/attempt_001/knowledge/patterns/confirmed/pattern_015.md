---
type: pattern
id: pattern_015
name: "ET(71)+1-opt ceiling at 75 is a hard structural barrier"
lifecycle: confirmed
confidence: 0.90
first_seen: generation_6
last_updated: generation_6
evidence: [gen006_explore_1_sol02, gen006_explore_1_sol03, gen006_explore_1_sol04, gen002_explore_1_sol03, gen002_explore_1_sol04]
related_ideas: [idea_011, idea_009, idea_002]
tags: [erdos-turan, local-search, ceiling, non-algebraic]
---

The ET(71) + greedy extension + 1-opt pipeline reliably converges to exactly 75 elements
for N=10000, and this ceiling is resistant to all tested escape strategies.

**Gen 6 evidence (30+ independent trials):**
- 2-opt on 75-element set: no improvement (sol02, timed out after partial search)
- LNS with k=2-15 random element removal + re-extend + 1-opt: always 75 (sol03)
- Randomized greedy from diverse starts (ET base, shuffled, ET-perturbed) + 1-opt: always 75 (sol04)

**Cross-generation evidence:**
- Gen 2: ET(71)+1-opt = 75 (first discovery)
- Gen 6: Confirmed across 3 solution variants with 30+ restarts total

The 75 plateau is extremely deep — it is not a weak local minimum escapable by moderate
perturbation. The entire basin of ET-based constructions with polynomial-time local search
converges to this point.

**Untested escape strategies that might work:**
- SA from the 75-element seed with longer time budget (5-10 min, not 27s)
- C-implemented 2-opt (full 2775-pair search, ~10-20 min in C)
- Starting from a non-ET base (e.g., Ruzsa-Lindström construction)
