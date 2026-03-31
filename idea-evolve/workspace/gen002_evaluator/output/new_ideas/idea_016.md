---
type: idea
id: idea_016
name: "8-Row int8 Accumulation Kernel"
lifecycle: active
confidence: 0.5
first_seen: generation_2
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002/experimentator_1/exp2b]
contradicted_by: []
related_ideas: [idea_009, idea_004, idea_001]
cluster: cluster_001
tags: [micro-kernel, 8-row, int8, register-pressure, avx512]
---

Combine 8-row kernel (idea_009, previously failed with int16) with int8
accumulation (idea_004). The key insight: int8 accumulation uses 1 zmm per
row instead of 2, halving register pressure and making the 8-row kernel feasible.

Register budget for 8-row int8:
- 8 zmm accumulators (1 per row)
- 1 zmm for vb (B tile)
- 2 zmm for vp, vn (shared/reused per row)
- Total: 11 zmm — well within the 32 zmm register file

Compared to current 4-row int16:
- Same 8 zmm total for accumulators
- 2x more rows per B load → 2x fewer B loads total
- `add_epi8` is 1 instruction (vs `cvtepi8_epi16 + add_epi16` = 2 per row)
- Reduces port 5 pressure by ~40% (eliminates vpmovsxbw + vextracti32x8)

Experimentator_1 confirmed int8 accumulation gives 11-13% improvement:
- Small (k=2): int16 5.07 µs → int8 4.86 µs (1.04x)
- Medium (k=4): int16 202.67 µs → int8 183.30 µs (1.11x)
- Large (k=7): int16 3669.63 µs → int8 3253.04 µs (1.13x)

**Correctness constraint**: int8 safe for k_bytes ≤ 15 (max ±120, within int8
±127). The correctness test uses k=256 (k_bytes=32), which overflows. Must
fall back to int16 or flush every 15 k-iterations for large k.

The 8-row variant has NOT been empirically tested yet. Research agent provided
the theoretical analysis and pseudocode. This is the second highest-priority
experiment after size-adaptive NT stores.

Pack_A must be restructured: groups of 8 rows instead of 4, storing 16 bytes
per k-byte (8 pos + 8 neg interleaved).
