---
id: idea_005
type: idea
name: "Backtracking with Pruning"
lifecycle: debunked
confidence: 0.05
first_seen: generation_0
last_updated: generation_6
last_confirmed_gen: 0
cluster: cluster_002
supported_by: []
contradicted_by: [gen006_explore_1_sol01]
related_ideas: [idea_003, idea_016]
tags: [search, backtracking, exhaustive, debunked]
---

DFS-based construction with aggressive pruning based on remaining valid candidates.

**Generation 6 — FIRST AND FINAL TEST (explore_1/sol01, score: 66):**
Systematic DFS with candidate-count upper bound pruning. Two phases:
1. Sequential ordering (0..N): finds exactly the greedy set (66 elements), then spends
   all remaining time (~27s) backtracking with zero improvement.
2. Randomized restarts (shuffled candidate order): also fails to exceed 66.

**Key insight:** The sequential DFS IS greedy — the forward pass produces the standard
greedy set, and backtracking from 66 elements at N=10000 explores a vanishingly small
fraction of the search tree in 27s. A C implementation (100x speedup) might reach 67-70
but cannot compete with algebraic constructions (105).

**Verdict: Debunked.** After 6 generations of being untested, the first empirical test
confirms backtracking is impractical for N=10000 in bounded time. The approach requires
exponential time to escape the greedy basin. Only potentially useful for small sub-problems
(N≤200) or with a C implementation + much longer time budgets.
