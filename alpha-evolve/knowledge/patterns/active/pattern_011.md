---
type: pattern
id: pattern_011
name: "LP constraint matrix construction is the bottleneck, not the LP solve"
lifecycle: active
confidence: 0.7
first_seen: generation_6
last_updated: generation_6
evidence: [gen006_full_1_sol01]
related_ideas: [idea_020, idea_016]
tags: [LP, constraint-matrix, engineering, scaling, bottleneck]
---

When implementing LP-based refinement at N=30000, the constraint matrix construction
(computing A_ub[j, k] = 2 * f[j - active_k] * dx for all tight constraint j and active
variable k) dominates runtime and memory, not the LP solve itself.

**Evidence (gen 6 full_1):**
- Python loop over (n_tight × n_active) pairs consumed ~7GB RAM and >19 minutes
  before being killed. The LP itself never ran.
- The mathematical formulation is sound — the engineering is the bottleneck.

**Solutions (from full_1's debrief):**
1. Work at reduced resolution (N=1000-3000), upsample descent direction
2. Batched FFT construction: compute f★e_k via batched FFT, O(K · N log N) total
3. Start with minimal LP (1-3 truly tight constraints via epsilon=1e-6)
4. Column generation to avoid computing all columns upfront

**Implication:** Any future LP attempt MUST address the construction bottleneck
before attempting the solve. The LP at N=30000 with 2000 active variables is feasible
for HiGHS but infeasible to construct naively in Python.
