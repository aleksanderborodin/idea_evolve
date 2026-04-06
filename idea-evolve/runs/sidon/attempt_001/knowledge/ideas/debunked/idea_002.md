---
type: idea
id: idea_002
name: "Local Search (Swap Neighborhood)"
lifecycle: debunked
confidence: 0.1
first_seen: generation_0
last_updated: generation_4
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_explore_2_sol06, gen003_explore_2_sol04]
related_ideas: [idea_010, idea_018]
cluster: cluster_002
tags: [search, local-search, swap, debunked]
---

Start from a greedy Sidon set. Define neighborhood: remove one element, try
adding a different one. Accept if the set grows or stays same size with more
room for future additions. Iterate until no improvement. Can be combined with
simulated annealing to escape local optima.

**Evidence summary across 4 generations**:
- LNS from greedy-66: 67 (gen 3, +1 only)
- LNS from spread-first-65: no improvement (gen 3)
- SA with violation relaxation from fib-68: no improvement (gen 3)
- All SA variants debunked (idea_010, idea_018)
- 8 central trials across all gens, best score 68

**Verdict (gen 4 consistency review)**: Downgraded from disputed to debunked. The maximum
gain from any local search variant is +1 element over the greedy seed. SA is confirmed
useless (idea_010, idea_018 both debunked). Pure local search provides negligible improvement
and is not a viable path to competitive scores. The +1 gain does not justify continued
investment when the gap to frontier is 33+ elements.
