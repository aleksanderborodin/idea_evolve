---
type: cluster
id: cluster_004
name: "Exact Methods (ILP / Constraint Programming)"
member_ideas: [idea_019]
best_score: 102
best_solution: gen004_full_1_sol01
status: active
last_updated: generation_4
---

This cluster contains ideas based on exact optimization methods — ILP, CP-SAT, and
constraint programming solvers.

**Gen 4 results (full_1)**:
- CP-SAT integer formulation validated: k ordered integer variables + AllDifferent on
  C(k,2) difference variables. Only O(k²) variables — 5356 for k=103.
- Proved Singer suboptimal for small N: q=7 (8→10), q=11 (12→13).
- k=103, N=10000: UNKNOWN after 600s. Neither found nor disproved.
- Previous gen 3 ILP attempt (CBC with O(N²) indicator variables) crashed with 661K
  constraints. The integer formulation is a massive improvement.

**Strategic significance**: This is the ONLY cluster with a credible path to 103+ that
doesn't depend on external databases. ILP is mathematically complete — given enough time,
it will either find 103 or prove it impossible.

**Next steps**:
1. Run CP-SAT for k=103 with 4+ hours and 16 workers
2. Try Gurobi (better LP relaxation bounds)
3. Study algebraic structure of "Singer+1" solutions at small N
4. Try indicator-variable maximization for N=500-1000 to find optimal sizes
