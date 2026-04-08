---
id: idea_024
type: idea
name: "VLNS — Very Large Neighborhood Search via CP-SAT"
lifecycle: active
confidence: 0.3
first_seen: generation_6
last_updated: generation_6
last_confirmed_gen: 6
cluster: cluster_004
supported_by: []
contradicted_by: []
related_ideas: [idea_019, idea_022, idea_020]
tags: [vlns, cp-sat, neighborhood-search, hybrid]
---

Fix most elements of the 105-mark set, use CP-SAT to find optimal replacements for the
remaining free elements. This decomposes the intractable k=106 problem into many smaller
sub-problems (e.g., fix 85 elements, solve for 21 free elements).

**Gen 6 results (full_1/sol03):** 9 trials with different removal patterns (random-15/20/25,
high-density-20, spread-20) all returned INFEASIBLE in <1 second.

**CRITICAL: Likely formulation bug, not genuine infeasibility.**
The `add_abs_equality(d, y[i] - fv)` creates a difference variable with domain [1, N]
(excluding fixed differences). During presolve, if y[i] = fv is still in the variable's
domain, the absolute difference is 0 — excluded by the [1,N] domain → INFEASIBLE.

**Fix needed:** Change cross-diff domain from [1,N] to [0,N] and add explicit `d >= 1`
constraint, or add `y[i] != fv` constraints before the abs constraint so they propagate
during presolve.

**Potential:** If the formulation bug is fixed, VLNS could efficiently search large
neighborhoods around the 105-mark set. Each sub-problem has only ~20 free variables
vs 106 for the full problem. Even finding alternative 105-element sets would be
valuable (different local optima may be extensible).

**Priority:** Fix formulation and retry with 50+ removal patterns before declaring this
approach dead.
