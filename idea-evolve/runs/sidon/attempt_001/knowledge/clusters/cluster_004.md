---
type: cluster
id: cluster_004
name: "Exact Methods (ILP / Constraint Programming)"
member_ideas: [idea_019, idea_024]
best_score: 105
best_solution: gen007_exploit_1_sol01
status: active
last_updated: generation_7
---

This cluster contains ideas based on exact optimization methods — ILP, CP-SAT, and
constraint programming solvers.

**Gen 7 consistency review update:**
- **idea_024 promoted to established** (was active). VLNS formulation confirmed correct by
  3 independent agents. 85+ trials with corrected formulation → ALL INFEASIBLE at 106, ALL
  OPTIMAL at 105. Gen 6 "formulation bug" diagnosis was wrong — infeasibility is genuine.
- **cpsat.py helper delivered** by experimentator_1. 3 functions: solve_sidon_cpsat,
  vlns_sidon, vlns_batch. Self-tested and verified. Resolves 3-generation request.

**Cumulative CP-SAT compute for k>=103:** ~7000s across gens 4-7. Zero feasible solutions
for k=106. VLNS proves INFEASIBLE in <0.01s (presolve-level). AllDifferent formulation
returns UNKNOWN.

**Cluster status: ACTIVE** — one untested formulation remains.

**Only remaining viable experiment:**
- **Binary variable maximize-k CP-SAT** (EXP-5): x_i in {0,1} for i=0..10000, maximize
  sum(x_i), warm-start from BEST_105. Risk: ~25M constraints may exceed memory. If
  k_max=105, this cluster is exhausted. If k_max=106, breakthrough. **Highest priority.**

**Lower-priority experiments:**
- Anti-algebraic CP-SAT (force <=52 overlap with BEST_105)
- VLNS from non-BEST_105 seeds (e.g., BEST_104 Singer q=103 targeting 106)
- Tabu search with swap-then-fill (research_1 identified as best untried heuristic)
- Alternative solvers (Gurobi, SCIP) — unlikely to be installed
