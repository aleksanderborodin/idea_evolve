---
type: idea
id: idea_004
name: "int8/int16 Accumulation (Deferred Widening)"
lifecycle: established
confidence: 0.95
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [explore_1/sol02, explore_1/sol03, explore_1/sol04, explore_1/sol05, explore_1/sol06, explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol02, full_1/sol03, full_1/sol04, gen002/experimentator_1/exp2b, gen003/exploit_1/sol02, gen003/explore_1/sol02, gen003/explore_2/sol04]
contradicted_by: [full_1/sol01]
related_ideas: [idea_001, idea_009, idea_016]
cluster: cluster_001
tags: [accumulation, int8, int16, widening]
---

The diff per byte (popcount_pos - popcount_neg) is at most ±8. For k_bytes ≤ 7,
the accumulated sum fits in int8 (max ±56) or int16 (max ±56, well within ±32767).
Accumulate in narrow types, widen to int32 only at the end after the k-loop.

**Gen003 confirmation:** All new competitive solutions continue to use int8
accumulation. The new best (exploit_1/sol02, 141.0 µs) uses int8 with periodic
flush every 15 k-iterations. Explore_1/sol02 (8-row, 168.35 µs) and explore_2/sol04
(4-row vpshufb, 341.78 µs) also use int8 successfully.

Experimentator_1 (gen003) additionally confirmed that keeping functions monolithic
(not splitting into helper functions) is critical — non-inlined helper functions
for flush logic caused 1.3-1.5x regression.

**Correctness constraint** (unchanged): The correctness test uses k=256 (k_bytes=32),
which overflows int8 accumulators (max ±256 > ±127). Solutions must flush every 15
k-iterations for large k.

Established with high confidence. Universal across all competitive solutions.
