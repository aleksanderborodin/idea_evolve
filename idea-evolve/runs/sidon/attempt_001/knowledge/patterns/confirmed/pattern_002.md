---
type: pattern
id: pattern_002
name: "Random-order greedy is worse than deterministic"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_2_sol01, gen001_full_1_sol01]
related_ideas: [idea_001, idea_009]
tags: [greedy, randomization, counterintuitive]
---

Random-order greedy (shuffling candidates before greedy construction) consistently produces
Sidon sets of 58-62 elements, significantly worse than the deterministic forward-scan greedy
(66 elements). This is counterintuitive — random restarts usually help in combinatorial
optimization.

Explanation: The deterministic greedy packs small numbers first, which minimizes the magnitude
of used differences. This is equivalent to the Erdos-Turan construction (idea_009) for p=67.
Random ordering disrupts this algebraic structure and wastes differences on large gaps.

Implication: Random restarts are not useful for this problem. Any improvement over 66 must
come from algebraic constructions or sophisticated search (SA, 2-opt+).
