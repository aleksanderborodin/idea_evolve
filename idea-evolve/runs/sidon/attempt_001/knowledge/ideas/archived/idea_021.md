---
id: idea_021
type: idea
name: "Beam Search Greedy"
lifecycle: archived
confidence: 0.2
first_seen: generation_5
last_updated: generation_6
last_confirmed_gen: 5
cluster: cluster_002
supported_by: [gen005_explore_1_sol01, gen005_explore_1_sol05, gen005_explore_1_sol07]
contradicted_by: []
related_ideas: [idea_015, idea_016, idea_003]
tags: [beam-search, greedy, ceiling-confirmed, archived]
---

Maintains k parallel partial Sidon sets, extending with best candidates. Seven variants
tested in gen 5 with k=30 to k=800.

Best result: **70 elements** (k=500, greedy candidate selection). k=800 produces identical
result — beam width saturates below 500 effective unique beams.

**Gen 6 consistency review**: Archived. Ceiling 70 confirmed and saturated. 35-element gap
to algebraic best (105) is structural. Cluster_002 exhausted. No further exploration warranted.
