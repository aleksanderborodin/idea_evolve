---
id: idea_019
type: idea
name: "CP-SAT / ILP Constraint Programming"
lifecycle: active
confidence: 0.35
first_seen: generation_4
last_updated: generation_7
last_confirmed_gen: 7
cluster: cluster_004
supported_by: [gen004_full_1_sol01, gen005_full_1_sol01]
contradicted_by: []
related_ideas: [idea_005, idea_008, idea_020, idea_022, idea_024]
tags: [exact-method, constraint-programming, ilp, cp-sat]
---

Uses Google OR-Tools CP-SAT solver with various formulations to find optimal Sidon sets.

**Gen 4-5:** AllDifferent formulation, k=103-106 decision problems. 6000s total compute,
all UNKNOWN. Proved Singer suboptimal for small N.

**Gen 6:** k=106 with hint (1200s, 16 workers) → UNKNOWN. Binary search on N → UNKNOWN
at all tested values. VLNS trials → INFEASIBLE (initially attributed to bug).

**Gen 7 — NEW EVIDENCE:**

1. **exploit_1: Binary VLNS formulation confirmed correct.** 85+ trials with corrected
   formulation (integer vars, domain [0,N]). All 106-targets INFEASIBLE. All 105-targets
   OPTIMAL in <0.1s. The INFEASIBILITY is genuine, not a formulation artifact.

2. **experimentator_1: cpsat.py helper delivered.** Three functions: `solve_sidon_cpsat`
   (binary or element formulation), `vlns_sidon` (corrected VLNS), `vlns_batch`. All
   self-tested and verified with real data. This addresses the 3-generation-old request
   for a reusable CP-SAT helper.

3. **full_1: No progress.** Session interrupted before code was written. The binary variable
   maximize formulation (EXP-5) remains untested.

4. **research_1: Literature supports VLNS infeasibility.** The code already had y[i]!=fv
   constraints. The fast INFEASIBLE reflects genuine combinatorial constraint, not a bug.

**Confidence reduced to 0.35.** Four generations of compute (gens 4-7) with zero improvement
beyond 105. The only untested formulation is the **binary variable maximize-k** approach
(EXP-5): x_i ∈ {0,1} for i=0..10000, maximize Σx_i, warm-start from BEST_105, 4h+ runtime.
This is the last viable CP-SAT experiment. If it returns k_max=105, the CP-SAT direction
is exhausted.
