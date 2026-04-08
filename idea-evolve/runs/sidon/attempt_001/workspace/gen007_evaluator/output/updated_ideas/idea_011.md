---
id: idea_011
type: idea
name: "Erdos-Turan Extension with Local Search"
lifecycle: active
confidence: 0.35
first_seen: generation_2
last_updated: generation_7
last_confirmed_gen: 7
cluster: cluster_002
supported_by: [gen002_explore_1_sol03, gen002_explore_1_sol04, gen006_explore_1_sol02, gen006_explore_1_sol03, gen006_explore_1_sol04, gen007_explore_1_sol03]
contradicted_by: []
related_ideas: [idea_009, idea_002, idea_022, idea_025]
tags: [erdos-turan, local-search, extension, non-algebraic]
---

Combines Erdos-Turan construction (p=71) with greedy extension and local search (1-opt,
2-opt, LNS, VLNS).

Best result: 75 elements (gen 2, confirmed gens 6 and 7).

**Gen 7 update (explore_1):**
- Ruzsa-Lindström primitive root p=71 (structurally different from quadratic ET) + VLNS: 75 (sol03)
- Both algebraic seed types (quadratic ET and exponential Ruzsa) converge to same 75 ceiling
- Multi-start with p=61 (70 after VLNS) and p=71 (75 after VLNS) both confirm ceiling

The 75 ceiling is confirmed by yet another algebraic seed type and multiple VLNS configurations.
This is now the confirmed structural barrier for all non-algebraic search from ~70-element
algebraic seeds, regardless of construction type (ET quadratic, Ruzsa exponential, or greedy).

**Confidence remains 0.35** — superseded by algebraic constructions (105) with a 30-element gap.
No further investment recommended.
