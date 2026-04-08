---
id: idea_024
type: idea
name: "VLNS — Very Large Neighborhood Search via CP-SAT"
lifecycle: established
confidence: 0.85
first_seen: generation_6
last_updated: generation_7
last_confirmed_gen: 7
cluster: cluster_004
supported_by: [gen007_exploit_1_sol01, gen007_experimentator_1]
contradicted_by: []
related_ideas: [idea_019, idea_022, idea_020]
tags: [vlns, cp-sat, neighborhood-search, hybrid, confirmed]
---

Fix most elements of the 105-mark set, use CP-SAT to find optimal replacements for the
remaining free elements. This decomposes the intractable k=106 problem into many smaller
sub-problems (e.g., fix 85 elements, solve for 21 free elements).

**Gen 6 results (full_1/sol03):** 9 trials with different removal patterns all returned
INFEASIBLE in <1s. Diagnosed as "formulation bug" (abs-equality domain conflict).

**Gen 7 — CRITICAL UPDATE: INFEASIBILITY IS GENUINE, NOT A BUG.**

Two independent agents (exploit_1, experimentator_1) confirmed:

1. **exploit_1** (corrected integer-variable formulation, domain [0,N]): 85+ trials,
   remove 5-55 elements, ALL INFEASIBLE for target 106. Validation: remove 50, target
   105 → OPTIMAL (recovers original elements exactly). The formulation is correct.

2. **experimentator_1** (cpsat.py helper, unified per-difference-value constraints):
   9 VLNS trials (rm=3,5,10), ALL OPTIMAL at 105 in <0.1s each. The corrected formulation
   works perfectly — it just can't find 106 elements.

**Key findings:**
- For k≤44 removed elements, EXACTLY k valid candidates exist — mathematically impossible
  to add more. The 105-mark set is uniquely rigid.
- For k=50-55, 60-174 candidates exist but the maximum Sidon subset among them is always
  exactly k (the removed elements).
- Binary VLNS proves INFEASIBLE in <0.01s — impossibility detected at presolve level.
- The gen6 "formulation bug" diagnosis was WRONG. The original code already had y[i]!=fv
  constraints. INFEASIBILITY is genuine.

**Lifecycle promoted to established** — the VLNS technique works correctly and is now
available as a reusable helper (cpsat.py). It confirms the 105-mark set's self-healing
property computationally with a correct formulation. VLNS from BEST_105 subsets cannot
reach 106 — the neighborhood is provably exhausted.

**Remaining question:** VLNS from a different starting set (not subset of BEST_105)
might behave differently. Untested.
