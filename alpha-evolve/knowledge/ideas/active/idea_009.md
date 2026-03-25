---
type: idea
id: idea_009
name: "Softplus reparameterization for non-negativity"
lifecycle: active
confidence: 0.6
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_full_1_sol03, gen001_full_1_sol04]
contradicted_by: []
related_ideas: [idea_005, idea_001]
cluster: cluster_001
tags: [reparameterization, softplus, non-negativity, constraint]
---

Instead of using relu(f) or bounds to enforce non-negativity, parameterize
f = softplus(raw_params) where raw_params are unconstrained. This ensures
f > 0 strictly (no dead gradients from relu's flat region at 0) and provides
smooth gradients everywhere.

**Evidence:**
- full_1/sol03 and sol04 (both top-2 solutions) use softplus reparameterization.
- explore_1/sol05 and sol07 use relu — also good but 0.005 worse than softplus solutions.
- explore_2/sol09 uses relu — 1.5182.

The evidence is suggestive but not conclusive: sol03's advantage over sol05 could
be due to smooth-max rather than softplus. A controlled experiment isolating softplus
vs relu with the same optimizer would clarify.
