---
type: idea
id: idea_021
name: "Triplet perturbation (integral-preserving multi-element moves)"
lifecycle: archived
confidence: 0.3
first_seen: generation_7
last_updated: generation_10
last_confirmed_gen: 9
supported_by: [gen007_explore_1_sol01, gen008_explore_1_sol01, gen008_exploit_1_sol01, gen009_explore_1_sol01]
contradicted_by: [gen008_exploit_2_sol01, gen009_exploit_1_sol01, gen010_explore_1_sol01, gen010_explore_2_sol01, gen010_exploit_2_sol01]
related_ideas: [idea_019, idea_014, idea_022]
cluster: cluster_001
tags: [triplet, perturbation, multi-element, integral-preserving, coordinate-descent, subsumed, archived]
---

Coordinated 3-element perturbation with constraint d1+d2+d3=0 (integral-preserving).

**ARCHIVED (gen 10 consistency review):** Fully subsumed by ultra-fine coordinate
descent (idea_019). Confidence below 0.7 threshold for established (0.6 -> 0.3).
5 contradictions vs 4 supports. Gen 10: 0 improvements across 3 independent sessions
(explore_1: 47k minimax trials, explore_2: 200k trials, exploit_2: 27k A/B test trials).
Cumulative gen 9-10: 0 improvements in 5 sessions when starting from ultra-fine-CD solutions.

Triplets only effective when starting from standard-delta-CD solutions (last positive
evidence: gen 9 explore_1, 150 improvements from standard CD baseline). Current frontier
solutions all have ultra-fine CD applied, making triplets permanently ineffective.

Pattern_020 (confirmed, 0.95) explains why: ultra-fine single-element CD captures the same
landscape features more effectively through non-integral-preserving mechanism (pattern_024).
