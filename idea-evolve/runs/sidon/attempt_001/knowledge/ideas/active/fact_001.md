---
id: fact_001
type: fact
name: "Greedy Baseline Score"
confidence: 1.0
first_seen: generation_0
last_confirmed_gen: 6
verified: true
source: user-provided, confirmed by dozens of solutions across all generations
tags: [baseline, greedy]
---

The simple greedy algorithm (add smallest valid element) produces a Sidon set
of size 66 for N=10000. This is the starting baseline.

**Gen 6 confirmation**: DFS/backtracking (idea_005) proved sequential DFS IS greedy,
producing the identical 66-element set. Verified independently across all 6 generations.

**Gen 6 consistency fix**: confidence upgraded to 1.0, verified set to true.
