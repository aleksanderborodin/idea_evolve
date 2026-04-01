---
type: idea
id: idea_007
name: "SIMD Packing (Vectorized pack_B)"
lifecycle: established
confidence: 0.85
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10]
contradicted_by: []
related_ideas: [idea_001, idea_013]
cluster: cluster_001
tags: [packing, simd, pack_b, avx512]
---

Replace scalar byte-by-byte pack_B loop with AVX-512 `_mm512_loadu_si512` /
`_mm512_storeu_si512`. For 64-column chunks of B, one zmm load + one zmm store
replaces 64 scalar byte copies per k-row.

This was one of the biggest single-step improvements in gen001. explore_1/sol07
introduced vectorized pack_B and jumped from 381.32 µs (sol04) to 306.60 µs —
a major improvement. The agent reported that pack_B was a bigger bottleneck than
the micro-kernel itself for medium/large sizes.

All subsequent top solutions (sol08-sol10) retained vectorized pack_B. The
improvement compounds with other optimizations: by reducing packing overhead,
the relative weight of micro-kernel compute increases, making micro-kernel
optimizations (int16 accum, ternarylogic) more impactful.

explore_1/sol10 also handles partial columns (< 64) via masked loads:
`_mm512_maskz_loadu_epi8(mask, ...)`. This is correct and handles edge cases.

pack_A remains scalar in all solutions. It could be vectorized too, but A is
much smaller (MC × k_bytes × 2 ≤ 64 × 7 × 2 = 896 bytes) so the payoff is
minimal.
