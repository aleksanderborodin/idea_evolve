---
type: idea
id: idea_009
name: "Softplus reparameterization for non-negativity"
lifecycle: established
confidence: 0.6
first_seen: generation_1
last_updated: generation_4
last_confirmed_gen: 4
supported_by: [gen001_full_1_sol03, gen001_full_1_sol04]
contradicted_by: [gen004_exploit_1_sol01, gen004_exploit_1_sol02, gen004_exploit_2_sol01]
related_ideas: [idea_005, idea_001, idea_017]
cluster: cluster_001
tags: [reparameterization, softplus, non-negativity, constraint, limitation]
---

Instead of using relu(f) or bounds to enforce non-negativity, parameterize
f = softplus(raw_params) where raw_params are unconstrained.

**Gen 1-3:** Standard in all top solutions. Provides smooth gradients and strict
positivity. Never isolated as an independent variable.

**Gen 4 update — MAJOR LIMITATION DISCOVERED:**
- When warm-starting from published solutions with near-zero elements (e.g., the
  AlphaEvolve 1319-element array), inv_softplus maps near-zero values to large
  negative raw_params. The softplus gradient is exponentially small in these
  regions, creating "dead zones" the optimizer cannot traverse.
- exploit_1 found that smooth-max Adam cannot improve the 1.5032 solution at all —
  score moved by only 3.8e-9 (floating-point noise).
- exploit_2's cubic spline upsample created oscillations in near-zero regions,
  suggesting the softplus parameterization is inappropriate for sparse solutions.

**Conclusion:** Softplus works well for gradient-descent from random initialization
(where values are typically far from zero) but is a bottleneck for warm-start
optimization of published solutions with sparse structure. Projected gradient
descent (idea_017) may be more appropriate for these cases.

Confidence maintained at 0.6 — still useful for random-init gradient descent,
but now known to be a limitation for warm-start optimization.
