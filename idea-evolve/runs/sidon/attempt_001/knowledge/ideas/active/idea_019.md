---
id: idea_019
type: idea
name: "CP-SAT / ILP Constraint Programming"
lifecycle: active
confidence: 0.4
first_seen: generation_4
last_updated: generation_6
last_confirmed_gen: 6
cluster: cluster_004
supported_by: [gen004_full_1_sol01, gen005_full_1_sol01]
contradicted_by: []
related_ideas: [idea_005, idea_008, idea_020, idea_022]
tags: [exact-method, constraint-programming, ilp, cp-sat]
---

Uses Google OR-Tools CP-SAT solver with k integer variables + AllDifferent on differences.
Proved Singer suboptimal for small N (q=7: 8→10 optimal, q=11: 12→13 optimal).

**Gen 5 results:** Three 600s CP-SAT phases for k=103 all UNKNOWN. Key insight: optimal
sets share almost no elements with Singer (3/8 overlap q=7, 1/12 overlap q=11).

**Gen 6 results (full_1) — significant new evidence:**
- k=106 with 105-mark hint, 1200s, 16 workers → UNKNOWN (no feasible solution found)
- k=104 verification (30s, 8 workers) → UNKNOWN (surprisingly, even with 105-element hint)
- k=106 with linearization_level=2, symmetry_level=2 (600s) → UNKNOWN
- Binary search on N: k=106 at N=10000, 10200, 10500, 11000, 12000, 15000 all UNKNOWN
- **VLNS (fix 85, solve for 21):** 9 trials all INFEASIBLE in <1s — likely formulation bug
  (abs-equality domain conflict in presolve, not genuine infeasibility)

**Gen 6 insights:**
1. k=106 difficulty is NOT primarily from tight N=10000 bound — still hard at N=15000
2. The AllDifferent formulation may be too hard for CP-SAT to make search progress
3. VLNS could work if formulation bug is fixed (domain [1,N] → [0,N] for cross-diffs)
4. 105-element hint doesn't help even for k=104 — hint propagation may be ineffective

**Confidence reduced to 0.4** — three generations of compute (gens 4-6) with zero progress.
Still the only viable path to 106+ but needs either much longer runs (4h+), fixed VLNS
formulation, or alternative solvers (Gurobi, SCIP).
