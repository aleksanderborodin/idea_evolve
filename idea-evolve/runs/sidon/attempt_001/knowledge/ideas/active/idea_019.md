---
type: idea
id: idea_019
name: "CP-SAT Integer Formulation (Constraint Programming)"
lifecycle: active
confidence: 0.6
first_seen: generation_4
last_updated: generation_4
last_confirmed_gen: 4
supported_by: [gen004_full_1_sol01]
contradicted_by: []
related_ideas: [idea_008, idea_005]
cluster: cluster_004
tags: [constraint-programming, ILP, exact, CP-SAT, ortools]
---

Use Google OR-Tools CP-SAT solver with an integer element formulation: k ordered integer
variables e_0 < e_1 < ... < e_{k-1} in {0,...,N}, C(k,2) difference variables d_{i,j} = e_j - e_i,
and a single AddAllDifferent constraint on all differences. This enforces the Sidon property
exactly. The formulation has only O(k²) variables — far more compact than indicator variable
formulations (which would need ~50M variables for N=10000, k=103).

**Generation 4 evidence (full_1)**:
- Validated at small N: found optimal solutions for N=56 (k=10, beating Singer's k=8) and
  N=132 (k=13, beating Singer's k=12). Singer is provably suboptimal for small N.
- At N=10000, k=103: ran 600s total (300s with Singer hint, 300s without). Status: UNKNOWN
  (neither found a solution nor proved infeasibility). The solver cannot handle this scale
  in 600s but did not prove 103 impossible.
- Singer 102-element hint warm-starts the search correctly.

**Critical insight**: CP-SAT returned UNKNOWN, not INFEASIBLE, for k=103. This means 103
elements in {0,...,10000} is not ruled out. A longer run (hours) with more workers or a
commercial solver (Gurobi/CPLEX) might resolve this.

**Limitations**: CP-SAT's branch-and-bound may not have tight enough LP relaxation bounds
for this problem. The search space is enormous even with the compact formulation.

**Next steps**:
1. Run k=103 for 4+ hours with 16 workers
2. Try Gurobi MIP formulation (better LP relaxation)
3. Study the algebraic structure of "Singer+1" solutions at small N (q=7, q=11)
   to find patterns that generalize to q=101
