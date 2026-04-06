---
type: idea
id: idea_001
name: "Randomized Greedy with Restarts"
lifecycle: debunked
confidence: 0.05
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 1
supported_by: []
contradicted_by: [gen001_explore_2_sol01, gen001_full_1_sol01, gen003_explore_2_sol01]
related_ideas: [idea_009, idea_015]
cluster: cluster_002
tags: [search, greedy, restarts, debunked]
---

The basic greedy algorithm always adds the smallest valid element, giving 66.
Try random orderings of candidates: shuffle the range [0, 10000] and greedily
add elements that don't violate the Sidon property. Run many restarts and keep
the best. Different random orderings explore different parts of the search space.

**Generation 1 evidence**: Random-order greedy consistently scores 58-62 elements,
significantly WORSE than deterministic greedy (66). Confirmed by explore_2 and full_1.

**Generation 3 evidence**: explore_2/sol01 confirmed again: 63 elements with 25 seconds
of random restarts. Still below deterministic greedy (66).

**Verdict**: Downgraded to debunked. Three generations of evidence confirm randomized
greedy is counterproductive. The deterministic forward scan has algebraic structure
(Erdos-Turan) that random ordering destroys. Fibonacci ordering (idea_015) is the correct
way to modify greedy candidate ordering — it achieves 69 by using exponential growth
structure rather than random shuffling.
