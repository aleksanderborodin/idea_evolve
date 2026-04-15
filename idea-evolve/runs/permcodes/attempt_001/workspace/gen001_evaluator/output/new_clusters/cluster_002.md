---
type: cluster
id: cluster_002
name: "Search Heuristics for Maximum Clique"
member_ideas: [idea_003, idea_005, idea_006]
best_score: 262
best_solution: gen000_baseline_sol01
status: active
last_updated: gen001
---

Iterative improvement methods (ILS, tabu search, simulated annealing) applied to the compatibility graph G(8,5). These methods complement algebraic approaches by exploring the full permutation space without group structure constraints.

fast_compatible_mask is critical infrastructure for all these methods — 23x speedup enables practical neighborhood evaluation.

Status: active but unvalidated. ILS and tabu search were assigned to agents in gen001 but no solutions were produced. The greedy baseline (262) shows these methods need significant work to compete with algebraic approaches.
