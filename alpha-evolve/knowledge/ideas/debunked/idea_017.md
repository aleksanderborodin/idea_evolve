---
type: idea
id: idea_017
name: "Projected gradient descent (direct f-space optimization)"
lifecycle: debunked
confidence: 0.1
first_seen: generation_4
last_updated: generation_7
last_confirmed_gen: 5
supported_by: []
contradicted_by: [gen005_exploit_1_sol01, gen005_exploit_2_sol01]
related_ideas: [idea_009, idea_001, idea_014, idea_019]
cluster: cluster_001
tags: [optimization, projected-gradient, non-negativity, f-space, debunked]
---

Instead of optimizing via softplus reparameterization, optimize the function values f
directly with a non-negativity projection after each gradient step.

**DEBUNKED after gen 5-7 evidence.**

All gradient variants tested and failed:
- **Adam on f directly:** gradient nearly uniform, worsened C at all learning rates.
- **Hard-max gradient:** too sparse (single argmax element), all lr failed.
- **Normalized gradient:** still failed.
- **Sensitivity-guided gradient:** corrupted by float32 (pattern_008).

The working variant (coordinate descent) was split into its own idea (idea_019) which
is now established at confidence 0.85. The original hypothesis ("softplus is the
bottleneck") was wrong — the optimization landscape itself is the barrier for ALL
gradient-based methods.

**Gen 7 update:** Demoted from disputed to debunked. The gradient variants have zero
remaining avenues. Coordinate descent (the partial success) is fully covered by idea_019.
Confidence lowered to 0.1.
