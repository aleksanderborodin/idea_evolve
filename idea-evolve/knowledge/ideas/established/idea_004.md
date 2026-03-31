---
type: idea
id: idea_004
name: "int8/int16 Accumulation (Deferred Widening)"
lifecycle: established
confidence: 0.95
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol02, explore_1/sol03, explore_1/sol04, explore_1/sol05, explore_1/sol06, explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol02, full_1/sol03, full_1/sol04]
contradicted_by: [full_1/sol01]
related_ideas: [idea_001, idea_009]
cluster: cluster_001
tags: [accumulation, int8, int16, widening]
---

The diff per byte (popcount_pos - popcount_neg) is at most ±8. For k_bytes ≤ 7,
the accumulated sum fits in int8 (max ±56) or int16 (max ±56, well within ±32767).
Accumulate in narrow types, widen to int32 only at the end after the k-loop.

This was one of the most impactful optimizations in gen001. full_1/sol01 accumulated
in int32 *inside* the k-loop using `_mm512_cvtepi8_epi32` + `_mm512_extracti32x4_epi32`
— 16 expensive operations per k-byte. Result: 602.29 µs (worse than baseline on
medium/large). full_1/sol02 switched to int8 accumulation across the k-loop and
widening once at the end: 339.09 µs (1.78x improvement from this single change).

The best solutions use two variants:
- **int8 accumulation** (full_1/sol02, full_1/sol04): `_mm512_add_epi8` in k-loop,
  `_mm512_cvtepi8_epi32` once after. Simpler, fewer registers.
- **int16 accumulation** (explore_1/sol10): `_mm512_cvtepi8_epi16` per k-step,
  `_mm512_add_epi16` in k-loop, then `_mm512_cvtepi16_epi32` at end. Uses 2 zmm
  accumulators per row (32 int16 each) to cover 64 columns.

Both approaches are valid. int8 is simpler; int16 gives more headroom for larger k.
Established with high confidence — the contrast between sol01 (int32-in-loop) and
sol02+ (deferred widening) is dramatic.
