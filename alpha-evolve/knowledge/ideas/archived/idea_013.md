---
type: idea
id: idea_013
name: "Arcsine initialization for coarse-to-fine"
lifecycle: archived
confidence: 0.4
first_seen: generation_3
last_updated: generation_7
last_confirmed_gen: 3
supported_by: [gen003_explore_2_sol01, gen003_explore_2_sol03, gen003_explore_2_sol04]
contradicted_by: []
related_ideas: [idea_003, idea_004, idea_012]
cluster: cluster_002
tags: [initialization, arcsine, coarse-to-fine, asymmetric, archived]
---

Initialize with an arcsine-weighted profile on a biased subinterval, then optimize
via coarse-to-fine + warm smooth-max.

**Gen 3 evidence:**
- Best result: C = 1.5090 (explore_2/sol01), marginal improvement over 1.5091 baseline.
- Arcsine dominates other init families at coarse scale in head-to-head (25-seed funnel).
- However, all init families converge to the same ~1.509 attractor basin.

**Gen 7 ARCHIVED:** Last confirmed gen 3 (4 generations stale). The pipeline frontier
is now at C=1.50286 via coordinate descent and triplet perturbation on published
solutions. Initialization strategies for gradient descent from random init are
irrelevant to the current approach, which starts from published arrays. Archiving
due to staleness and irrelevance to frontier.
