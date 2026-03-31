---
type: idea
id: idea_009
name: "Wider Micro-Kernel 8x64"
lifecycle: disputed
confidence: 0.4
first_seen: generation_0
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002/explore_2/sol01]
contradicted_by: [explore_1/sol03]
related_ideas: [idea_001, idea_004, idea_016]
cluster: cluster_001
tags: [micro-kernel, 8x64, register-pressure, avx512]
---

With 32 zmm registers (AVX-512), process 8 rows of A at once instead of 4,
halving the number of micro-kernel calls and B loads.

Gen001 failure with int16 accumulators (8 rows × 2 zmm each = 16 zmm for
accumulators alone → register spilling) is well documented.

**Gen002 updates:**
- explore_2/sol01 used 8-row processing (jc-outer, int16): 207.32 µs — better
  than some 4-row variants but not competitive with best (148 µs)
- Research agent provided theoretical analysis showing 8-row int8 kernel uses
  only 11 zmm total — well within register budget
- Experimentator_1 confirmed int8 accumulation eliminates the register pressure
  problem

The 8-row int8 variant (idea_016) remains **untested empirically**. This is the
second highest priority experiment after NT stores. The theoretical argument is
strong: 2x fewer B loads, 40% less port 5 pressure, 1 zmm per row instead of 2.

Disputed: the 8-row concept is sound but no implementation has beaten 4-row yet.
The specific failure mode (register pressure with int16) is now understood and
the int8 solution is proposed but unverified.
