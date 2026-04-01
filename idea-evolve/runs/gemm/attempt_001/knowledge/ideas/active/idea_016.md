---
type: idea
id: idea_016
name: "8-Row int8 Accumulation Kernel"
lifecycle: active
confidence: 0.6
first_seen: generation_2
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen002/experimentator_1/exp2b, gen003/explore_1/sol02]
contradicted_by: [gen003/exploit_1/sol04, gen003/exploit_1/sol05]
related_ideas: [idea_009, idea_004, idea_001]
cluster: cluster_001
tags: [micro-kernel, 8-row, int8, register-pressure, avx512]
---

Combine 8-row kernel (idea_009) with int8 accumulation (idea_004). The key insight:
int8 accumulation uses 1 zmm per row instead of 2, halving register pressure and
making the 8-row kernel feasible.

**Gen003 first empirical results:**

Explore_1/sol02 implemented the 8-row int8 kernel: **168.35 µs** (small=5.24,
med=283.62, large=3212.90). This is the **best 8-row result ever**, significantly
better than gen001's 8-row int16 attempt (493 µs) and gen002's 8-row direct-B
attempt (207 µs).

Compared to the 1-row baseline (147.26 µs):
- Small: 5.24 vs 3.69 µs (42% worse — 8 row setup overhead)
- Medium: 283.62 vs 225.55 µs (26% worse — C write scatter)
- Large: 3212.90 vs 3841.72 µs (**16% better** — B-load amortization wins)

**C write scatter is the critical issue.** Writing 8 rows per j-block means
store addresses jump by m×4 bytes between rows. For large (m=65536), that's
256 KB between stores, destroying L1 effectiveness. Exploit_1 confirmed this
independently: sol04 (8-row with all acc32 upfront) got 399 µs, sol05 (deferred
flush) got 340 µs — both much worse than 1-row.

The 4-row variant from explore_2's vpshufb experiments also showed consistent
multi-row benefit for large: 1.55x medium, 1.67x large improvement from B-load
amortization. This suggests **4-row may be the sweet spot** — enough B sharing
to help large without excessive C write scatter.

**Key open question:** Can column-blocked writes (process NC columns for all 8/4
rows before moving to next column block) solve the C write scatter? This would
keep C output tiles in L1 while maintaining B-load sharing.
