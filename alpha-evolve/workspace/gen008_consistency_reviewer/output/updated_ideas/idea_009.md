---
type: idea
id: idea_009
name: "Softplus reparameterization for non-negativity"
lifecycle: archived
confidence: 0.4
first_seen: generation_1
last_updated: generation_8
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

**Gen 8 ARCHIVED:** Confidence was 0.5 with 4 contradicting solutions vs 2 supporting.
Below the 0.7 threshold for established lifecycle. The frontier (coord descent, triplets,
quadruplets) operates directly in f-space without softplus. Softplus is only relevant
for gradient descent from random init, which caps at C~1.509. Archiving due to:
- Confidence below established threshold (0.5 < 0.7)
- More contradictions (4) than supports (2)
- 4 generations stale (last_confirmed_gen: 4)
- Zero relevance to current frontier
