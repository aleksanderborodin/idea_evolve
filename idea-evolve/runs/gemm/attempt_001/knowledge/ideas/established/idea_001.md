---
type: idea
id: idea_001
name: "AVX-512 Micro-Kernel with Hardware Popcount"
lifecycle: established
confidence: 0.95
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol01, explore_1/sol02, explore_1/sol03, explore_1/sol04, explore_1/sol05, explore_1/sol06, explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol01, full_1/sol02, full_1/sol03, full_1/sol04]
contradicted_by: []
related_ideas: [idea_002, idea_004, idea_007, idea_008, idea_009, idea_011]
cluster: cluster_001
tags: [avx512, micro-kernel, popcount, bitalg]
---

Replace the 6-instruction LUT-based popcount (`vpshufb` + masks) with a single
`_mm512_popcnt_epi8()` instruction (AVX512_BITALG). Process 64 bytes of B per
iteration instead of 32 (AVX2). Micro-kernel shape becomes 4x64 (4 rows of A,
64 columns of B).

This is the foundational optimization of generation 1. Every successful solution
uses it. The first solution to apply it (explore_1/sol01, 654.75 µs) already
improved over baseline on small sizes, though medium/large regressed due to
int32-in-hot-loop widening overhead. Once combined with int8/int16 accumulation
(idea_004) and other optimizations, the AVX-512 popcount kernel achieves up to
5.20x speedup (explore_1/sol10, 148.18 µs).

Evidence is overwhelming: all 14 valid solutions use this idea, and the best
(148.18 µs) is 5.20x faster than the AVX2 baseline (770 µs). Established with
high confidence.
