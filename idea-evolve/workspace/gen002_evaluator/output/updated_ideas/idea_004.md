---
type: idea
id: idea_004
name: "int8/int16 Accumulation (Deferred Widening)"
lifecycle: established
confidence: 0.95
first_seen: generation_0
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [explore_1/sol02, explore_1/sol03, explore_1/sol04, explore_1/sol05, explore_1/sol06, explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol02, full_1/sol03, full_1/sol04, gen002/experimentator_1/exp2b]
contradicted_by: [full_1/sol01]
related_ideas: [idea_001, idea_009, idea_016]
cluster: cluster_001
tags: [accumulation, int8, int16, widening]
---

The diff per byte (popcount_pos - popcount_neg) is at most ±8. For k_bytes ≤ 7,
the accumulated sum fits in int8 (max ±56) or int16 (max ±56, well within ±32767).
Accumulate in narrow types, widen to int32 only at the end after the k-loop.

**Gen002 quantified data (experimentator_1 isolated measurements):**

| Size | int16 (µs) | int8 (µs) | Speedup |
|------|-----------|----------|---------|
| small (k=2) | 5.07 | 4.86 | 1.04x |
| medium (k=4) | 202.67 | 183.30 | **1.11x** |
| large (k=7) | 3669.63 | 3253.04 | **1.13x** |

int8 is strictly better than int16 for benchmark sizes. The improvement comes
from eliminating vpmovsxbw + vextracti32x8 widening ops from the inner loop,
which experimentator_1's assembly analysis showed consume ~40% of port 5
throughput.

**Correctness constraint (gen002 discovery):** The correctness test uses
k=256 (k_bytes=32), which overflows int8 accumulators (max ±256 > ±127).
Solutions must fall back to int16 or flush every 15 k-iterations.
explore_1 handled this with a periodic flush approach.

All gen002 row-streaming solutions (explore_1) use int8 accumulation with a
flush mechanism for large k. Established with high confidence.
