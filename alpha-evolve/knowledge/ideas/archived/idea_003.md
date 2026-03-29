---
type: idea
id: idea_003
name: "Function shape priors"
lifecycle: archived
confidence: 0.3
first_seen: generation_0
last_updated: generation_7
last_confirmed_gen: 3
supported_by: [gen001_explore_1_sol05, gen001_full_1_sol03]
contradicted_by: [gen001_explore_1_sol01, gen001_explore_2_sol01, gen001_explore_2_sol07]
related_ideas: [idea_006, idea_008, idea_013]
cluster: cluster_002
tags: [initialization, shape, prior, gaussian, hann, archived]
---

Initialize with known function families that have good autoconvolution properties:
Gaussians, bump functions, cosine windows, B-splines. Use these as starting
points for optimization rather than flat/random initialization.

**Gen 1 evidence is mixed:**
- Gaussian initialization (explore_1/sol01): 1.5207 — WORSE than flat+noise baseline.
- Hann window (explore_2/sol01): 3.0 — terrible.
- Gaussian mixture K=8 (explore_2/sol07): 1.5801 — over-parameterized.
- DIVERSE random bumps as seeds (explore_1/sol05, full_1/sol03) worked well
  when combined with multi-restart.

**Gen 3 update:** Arcsine initialization (idea_013) emerged as the best single
shape prior at coarse scale, but all init families converge to the same ~1.509
attractor basin.

**Gen 7 ARCHIVED:** Last confirmed gen 3. The pipeline frontier is now at C=1.50286
via coordinate descent and triplet perturbation on published solutions. Shape priors
are irrelevant to the current optimization approach (they apply only to gradient
descent from random init, which caps at C~1.509). Archiving due to staleness and
irrelevance to frontier.
