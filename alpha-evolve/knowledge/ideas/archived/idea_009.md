---
type: idea
id: idea_009
name: "Softplus reparameterization for non-negativity"
lifecycle: archived
confidence: 0.5
first_seen: generation_1
last_updated: generation_9
last_confirmed_gen: 4
supported_by: [gen001_full_1_sol03, gen001_full_1_sol04]
contradicted_by: [gen004_exploit_1_sol01, gen004_exploit_1_sol02, gen004_exploit_2_sol01, gen006_exploit_2_sol01]
related_ideas: [idea_005, idea_001, idea_017, idea_019]
cluster: cluster_001
tags: [reparameterization, softplus, non-negativity, constraint, limitation, archived]
---

Instead of using relu(f) or bounds to enforce non-negativity, parameterize
f = softplus(raw_params) where raw_params are unconstrained.

**Gen 1-3:** Standard in all gradient-descent solutions. Provides smooth gradients
and strict positivity.

**Gen 4 MAJOR LIMITATION:** inv_softplus maps near-zero values to large negative
raw_params with exponentially small gradients, creating "dead zones."

**Gen 6 inv_softplus bug:** Default clip_min=-10 causes +5.66e-04 round-trip error
for near-zero elements. Fixed with clip_min=-20.

**Gen 9 ARCHIVED (consistency review):** Confidence 0.5 is below the 0.7 threshold
for "established" lifecycle. 4 contradictions vs 2 supports. The frontier
(C~1.5029) uses coordinate descent directly in f-space without softplus.
Softplus is only relevant for gradient descent from random init, which caps at
C~1.509. Same archival rationale as idea_003 (shape priors) and idea_013
(arcsine init) — valid for the superseded gradient-descent paradigm, irrelevant
to the current frontier.
