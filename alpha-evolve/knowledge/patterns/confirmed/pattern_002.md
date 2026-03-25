---
type: pattern
id: pattern_002
name: "Multi-scale coarse-to-fine consistently beats single-resolution"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol04, gen001_explore_1_sol05, gen001_explore_1_sol06, gen001_explore_1_sol09, gen001_explore_1_sol11, gen001_explore_1_sol12]
related_ideas: [idea_004, idea_002]
tags: [multi-scale, performance]
---

Solutions using multi-scale optimization (N=600->N=2000) consistently score 1.516-1.518,
while single-resolution solutions at N=600 score 1.525+ and single-resolution at N=1000-1200
score 1.518-1.521.

The coarse phase at N=600 with 40k steps finds the right function shape efficiently.
Upsampling via linear interpolation preserves the shape. The fine phase at N=2000 with
50-80k steps provides precision improvement. This two-phase approach is strictly dominant
over single-resolution optimization at any N tested.
