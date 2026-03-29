---
type: idea
id: idea_022
name: "Quadruplet perturbation (4-element integral-preserving moves)"
lifecycle: archived
confidence: 0.3
first_seen: generation_8
last_updated: generation_10
last_confirmed_gen: 8
supported_by: [gen008_explore_1_sol01]
contradicted_by: [gen009_exploit_1_sol01, gen009_exploit_2_sol01, gen010_explore_2_sol01, gen010_exploit_2_sol01]
related_ideas: [idea_021, idea_019, idea_014]
cluster: cluster_001
tags: [quadruplet, perturbation, multi-element, integral-preserving, higher-order, archived]
---

Coordinated 4-element perturbation with constraint d1+d2+d3+d4=0 (integral-preserving).

**ARCHIVED — subsumed by ultra-fine coordinate descent (idea_019).**

**Gen 10 evidence:**
- explore_2: 50k quadruplet trials → **0 improvements**
- exploit_2 (A/B test Path B): ~3k quadruplet trials → **0 improvements**
- exploit_2 also scored gen9 checkpoint (ckpt_quad_5.npy): C = 1.5028628684790137,
  equal to gen8 best. The 50k momentum quadruplet trials from gen9 produced zero improvement.

**Cumulative gen 9-10 evidence:** 0 improvements across 4 independent sessions. Like
triplets, quadruplets are only effective on standard-delta-CD solutions (gen 8 evidence).
All current frontier solutions have ultra-fine CD applied, making quadruplets useless.

**Confidence lowered to 0.3. ARCHIVED** due to complete subsumption by ultra-fine CD and
5 consecutive null results across 2 generations.
