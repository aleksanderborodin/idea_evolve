---
type: idea
id: idea_003
name: "Function shape priors"
lifecycle: active
confidence: 0.5
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen001_explore_1_sol05, gen001_full_1_sol03]
contradicted_by: [gen001_explore_1_sol01, gen001_explore_2_sol01, gen001_explore_2_sol07]
related_ideas: [idea_006, idea_008, idea_013]
cluster: cluster_002
tags: [initialization, shape, prior, gaussian, hann]
---

Initialize with known function families that have good autoconvolution properties:
Gaussians, bump functions, cosine windows, B-splines. Use these as starting
points for optimization rather than flat/random initialization.

**Gen 1 evidence is mixed:**
- Gaussian initialization (explore_1/sol01): 1.5207 — WORSE than flat+noise baseline.
  Symmetric Gaussians converge to symmetric local minima with C >= 2 before breaking symmetry.
- Hann window (explore_2/sol01): 3.0 — terrible. Symmetric and concentrated.
- Gaussian mixture K=8 (explore_2/sol07): 1.5801 — over-parameterized, hard to optimize.
- However, DIVERSE random bumps as seeds (explore_1/sol05, full_1/sol03) worked well
  when combined with multi-restart — the shape prior is useful as part of a diverse
  seed pool, not as a single initialization.

Key insight: No single shape prior is reliably better than flat+noise. The value
is in diversity of initializations across multiple restarts.

**Gen 3 update:** Arcsine initialization (idea_013) emerged as the best single
shape prior at coarse scale, but the advantage over Gaussian is marginal (1.5090
vs 1.5091). All init families converge to the same ~1.509 attractor basin.
