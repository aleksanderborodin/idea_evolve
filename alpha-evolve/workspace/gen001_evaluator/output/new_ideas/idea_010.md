---
type: idea
id: idea_010
name: "Softplus/exp reparameterization"
lifecycle: active
confidence: 0.5
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: []
contradicted_by: []
related_ideas: [idea_001]
cluster: cluster_001
tags: [parameterization, gradient, reparameterization]
---

Replace ReLU projection (f = relu(g)) with softplus (f = log(1+exp(g))) or exp (f = exp(g))
to maintain gradient signal for all parameter values. ReLU kills gradients when g < 0,
effectively pruning grid points mid-optimization.

Research_1 identified this as "the single most important change" alongside symmetry enforcement.

Gen 1 evidence: explore_1/sol01 and sol02 used softplus reparameterization with L-BFGS but
scored poorly (1.69-1.81). However, this was confounded with L-BFGS from cold start being
bad overall. No solution tested softplus + Adam to isolate the reparameterization effect.

All top-scoring solutions in gen 1 used the standard ReLU approach (relu after optimization).
The reparameterization hypothesis is untested in isolation — high priority for gen 2.
