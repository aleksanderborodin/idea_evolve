---
type: idea
id: idea_017
name: "Projected gradient descent (direct f-space optimization)"
lifecycle: active
confidence: 0.3
first_seen: generation_4
last_updated: generation_4
last_confirmed_gen: 4
supported_by: []
contradicted_by: []
related_ideas: [idea_009, idea_001, idea_014]
cluster: cluster_001
tags: [optimization, projected-gradient, non-negativity, f-space]
---

Instead of optimizing via softplus reparameterization (raw_params → softplus → f),
optimize the function values f directly with a non-negativity projection (clamp to 0)
after each gradient step. This avoids the vanishing-gradient problem in near-zero
regions where softplus gradient is negligible.

**Motivation (gen 4):**
- exploit_1 discovered that the AlphaEvolve 1319-element array has many near-zero
  elements where softplus gradient vanishes. inv_softplus maps these to large negative
  raw_params, creating a "dead zone" the optimizer cannot move through.
- All warm-start attempts using softplus reparameterization failed to improve the
  1.5032 solution — the parameterization itself may be the bottleneck.
- exploit_1 suggested: "optimize f directly with non-negativity projection (clamp to 0)
  instead of softplus reparameterization."

**Not yet tested.** Priority experiment for gen 5.

**Variants to test:**
1. Adam on f directly, clamp to 0 after each step, very low lr (1e-5-1e-6)
2. Coordinate descent: perturb one f[i] at a time, keep improvements
3. Sensitivity-guided: compute ∂C/∂f[i], optimize only top-50 most sensitive elements
