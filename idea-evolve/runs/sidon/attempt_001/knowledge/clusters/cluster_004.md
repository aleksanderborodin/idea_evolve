---
type: cluster
id: cluster_004
name: "Exact Methods (ILP / Constraint Programming)"
member_ideas: [idea_019, idea_024]
best_score: 102
best_solution: gen004_full_1_sol01
status: active
last_updated: generation_6
---

This cluster contains ideas based on exact optimization methods — ILP, CP-SAT, and
constraint programming solvers.

**Gen 6 results (full_1) — major new evidence:**

1. **CP-SAT k=106 (1200s, 16 workers, 105-mark hint):** UNKNOWN. No feasible solution.
2. **k=104 verification (30s):** UNKNOWN — surprisingly hard even with full hint.
3. **Binary search on N:** k=106 UNKNOWN at N=10000, 10200, 10500, 11000, 12000, 15000.
   Difficulty is inherent to k=106, not driven by tight N bound.
4. **VLNS (idea_024, NEW):** Fix 85 elements, solve for 21 free → all 9 trials INFEASIBLE
   in <1s. **Likely formulation bug** (abs-equality domain conflict), not genuine infeasibility.

**Cumulative CP-SAT compute for k≥103:** ~6000s across gens 4-6, zero feasible solutions found.

**New member: idea_024 (VLNS)** — decompose intractable k=106 into smaller sub-problems.
Promising concept but needs formulation fix before real testing.

**Next steps (priority order):**
1. Fix VLNS formulation bug and retry with 50+ patterns
2. Overnight CP-SAT k=106 (4h+, 16 workers)
3. CP-SAT maximize formulation (find max k, not decision for fixed k)
4. Alternative solvers: Gurobi, SCIP, HiGHS
5. VLNS with maximize objective (find max elements given fixed subset)
