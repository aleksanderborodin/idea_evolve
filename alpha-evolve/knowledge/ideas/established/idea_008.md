---
type: idea
id: idea_008
name: "Skip KC Tiling for Small k"
lifecycle: established
confidence: 0.9
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol01, explore_1/sol02, explore_1/sol03, explore_1/sol04, explore_1/sol05, explore_1/sol06, explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol01, full_1/sol02, full_1/sol03, full_1/sol04]
contradicted_by: []
related_ideas: [idea_002, idea_005, idea_010]
cluster: cluster_002
tags: [tiling, kc-loop, simplification]
---

When k_bytes ≤ 7, the entire k-dimension fits in registers. The KC loop always
has exactly one iteration. Remove the KC-tiling overhead entirely — just iterate
over m-tiles and n-tiles directly, setting kc = k_bytes.

All gen001 solutions implicitly use this: none implement a KC loop. The outer
loop structure is jc → ic → jr → ir with kc = k_bytes throughout. Research
Finding 5 confirmed this is correct: entire B matrix (max 448 KB for large) fits
in L2, and A always fits in L1.

This simplification removes one loop level and eliminates unnecessary buffer
management. Combined with the tiny k values (2-7 bytes), the micro-kernel's
k-loop is the only remaining inner loop. Established — all evidence supports it.
