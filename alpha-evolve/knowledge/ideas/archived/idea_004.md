---
type: idea
id: idea_004
name: "Multi-scale optimization (coarse-to-fine)"
lifecycle: archived
confidence: 0.4
first_seen: generation_1
last_confirmed_gen: 3
supported_by: [gen002_explore_1_sol03, gen002_explore_1_sol02, gen003_explore_2_sol01, gen003_explore_2_sol03, gen003_explore_2_sol04]
contradicted_by: [gen002_explore_1_sol01, gen003_explore_1_sol01, gen003_explore_1_sol02, gen003_explore_1_sol03, gen004_exploit_2_sol01, gen005_explore_1_sol01, gen005_explore_1_sol02, gen005_explore_1_sol03, gen005_explore_1_sol04]
related_ideas: [idea_007, idea_013, idea_002]
cluster: cluster_002
tags: [coarse-to-fine, multi-scale, upsampling]
---

Start with low resolution, optimize, then upsample and refine. Best result C=1.5090
(gen 3, with warm fine stage + smooth-max + arcsine init). 9 contradictions vs 5
supports across gens 1-5.

**Gen 10 ARCHIVED:** Stale since gen 5. Only relevant to gradient-descent paradigm
which caps at C~1.509. Current frontier uses published solutions (N=30k) +
coordinate descent. Coarse-to-fine is inapplicable to the published-solution paradigm.

**Gen 11 consistency review:** Confidence reduced from 0.75 to 0.4. The 9:5
contradiction ratio and 6+ gen staleness do not justify 0.75. Archived status
confirmed.
