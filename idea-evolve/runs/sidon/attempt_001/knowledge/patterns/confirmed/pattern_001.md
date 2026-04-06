---
type: pattern
id: pattern_001
name: "Greedy-66 is a strict 1-opt local optimum"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_2_sol03, gen001_explore_2_sol04, gen001_explore_2_sol05, gen001_full_1_sol01]
related_ideas: [idea_002, idea_009]
tags: [landscape, local-optimum, greedy]
---

The standard greedy Sidon set (66 elements, built by adding the smallest valid element)
is a strict local optimum under 1-opt (single element swap). Removing any single element
from the greedy-66 set leaves exactly 1 available candidate — the removed element itself.
No single-element replacement improves the set.

Evidence from multiple agents: explore_2 confirmed via exhaustive single-removal scan
(sol03, sol05). full_1 independently verified: "after removing any single element, only 1
candidate becomes available." This explains why simple local search fails to improve on 66.

2-opt CAN escape: explore_2/sol04 found a 67-element set by removing 2 elements and adding 3.
But the improvement is marginal (+1).
