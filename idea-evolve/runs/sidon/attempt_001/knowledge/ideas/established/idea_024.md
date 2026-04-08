---
name: "VLNS - Very Large Neighborhood Search via CP-SAT"
type: idea
lifecycle: established
confidence: 0.85
first_seen: generation_6
last_updated: generation_7
last_confirmed_gen: 7
cluster: cluster_004
supported_by:
  - gen006_full_1_sol03
  - gen007_exploit_1_sol01
  - gen007_experimentator_1
contradicted_by: []
related_ideas:
  - idea_019
  - idea_022
  - idea_020
tags:
  - vlns
  - cp-sat
  - neighborhood-search
  - hybrid
  - confirmed
---

Fix most elements of 105-mark set, use CP-SAT to find optimal replacements for remaining free elements.

**Gen 6:** 9 trials all returned INFEASIBLE, diagnosed as "formulation bug." **Diagnosis was WRONG** — infeasibility is genuine (confirmed gen 7 by 3 independent agents).

**Gen 7 results:**
- exploit_1 (corrected formulation, integer vars, domain [0,N]): 85+ trials, remove 5-55 elements, ALL INFEASIBLE for target 106. Remove 50, target 105 -> OPTIMAL. Binary VLNS proves INFEASIBLE in <0.01s (presolve-level).
- experimentator_1 (cpsat.py helper, unified per-difference constraints): 9 VLNS trials, ALL OPTIMAL at 105 in <0.1s. Caught and fixed free-to-free diff collision bug during development.
- research_1: Read gen6 code, confirmed y[i]!=fv constraints already present.

**Key finding:** For k<=44 removed elements, EXACTLY k valid candidates exist — mathematical impossibility to add more. The 105-mark set is UNIQUE optimal from any of its subsets.

**Remaining question:** VLNS from different starting set (e.g., Singer q=103 104-mark) targeting 106 is untested. If also INFEASIBLE, strengthens F_2(10000)=105 claim.
