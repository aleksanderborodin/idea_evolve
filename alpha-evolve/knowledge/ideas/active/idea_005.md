---
type: idea
id: idea_005
name: "Regularization approaches"
lifecycle: active
confidence: 0.4
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 0
supported_by: []
contradicted_by: []
related_ideas: [idea_001, idea_007]
cluster: cluster_001
tags: [regularization, smoothness, constraints]
---

Add regularization terms to the objective: smoothness penalties, sparsity,
symmetry enforcement. These may help the optimizer avoid local minima
with high C values.

Not directly tested in gen 1. However, the softplus reparameterization used
in full_1/sol03 (best solution, C=1.5108) is a form of implicit regularization —
it ensures strict positivity and smooth gradients. The graduated smoothing
(log-sum-exp temperature annealing) in sol03 is also a regularization approach
applied to the max operator itself, not to the function. Both were highly effective.

The explicit smoothness/sparsity penalties remain untested. Scale invariance
(C(alpha*f) = C(f)) means the optimizer should normalize periodically — this
is an implicit constraint that was not widely adopted in gen 1.
