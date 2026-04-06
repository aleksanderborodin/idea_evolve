---
type: idea
id: idea_011
name: "Erdos-Turan Extension with Local Search"
lifecycle: active
confidence: 0.6
first_seen: generation_2
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002_explore_1_sol02, gen002_explore_1_sol03, gen002_explore_1_sol04]
contradicted_by: []
related_ideas: [idea_009, idea_002, idea_003]
cluster: cluster_002
tags: [algebraic, erdos-turan, local-search, hybrid, non-singer]
---

Combine the Erdos-Turan construction with greedy extension and 1-opt local search:
1. Build ET(71) base: 70 elements in {143, ..., 9941}.
2. Greedy extend over all {0, ..., 10000}: adds 4 elements to reach 74.
3. 1-opt swap search: remove each element, re-extend greedily. Accept if net positive. Reaches 75.

**Evidence**: explore_1/sol02 reached 74 (greedy only), sol03 and sol04 both reached 75
(1-opt). All 25 random restarts of randomized greedy + 1-opt also converge to 75, confirming
75 is a robust local optimum for ET-seeded approaches.

**Significance**: Best non-Singer result. Demonstrates that ET(71) is a stronger seed than
raw greedy (66→75 vs 66→68 with SA). However, 75 is far below Singer q=101's 102.

**Use case**: Alternative baseline for diversity. Not competitive with Singer for score maximization.
