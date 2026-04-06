---
type: pattern
id: pattern_004
name: "99-to-100 barrier is robust across perturbation approaches"
lifecycle: active
confidence: 0.7
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04]
related_ideas: [idea_007, idea_008, idea_010]
tags: [barrier, frontier, singer]
---

Three solutions (explore_1/sol02-04) all reached 99 elements via Singer perturbation but
none broke through to 100. Combined search time: ~280 seconds across different strategies
(small perturbation k=1-3, large perturbation k≤15, targeted blocker removal). All converged
to 99.

This suggests the 99-element basin around the Singer q=97 set is a robust local optimum
under greedy perturbation. Breaking to 100 likely requires either:
1. A different base construction (Singer q=101 truncation, idea_008)
2. A non-greedy search method that accepts temporary size decreases (SA, idea_010)
3. A fundamentally different algebraic approach

The barrier may not be fundamental — the theoretical upper bound for N=10000 is ~109
(not ~102 as initially believed). There is substantial room between 99 and 109.
