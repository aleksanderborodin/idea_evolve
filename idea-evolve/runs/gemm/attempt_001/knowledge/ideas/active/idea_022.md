---
type: idea
id: idea_022
name: "4-Row B-Load Amortization Kernel"
lifecycle: active
confidence: 0.6
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen003/explore_2/sol04, gen003/explore_1/sol02]
contradicted_by: []
related_ideas: [idea_009, idea_016, idea_014]
cluster: cluster_001
tags: [multi-row, 4-row, B-amortization, kernel]
---

Process 4 rows of A per B load instead of 1 (current best) or 8 (too much C scatter).
Each B cache line (64 bytes) is loaded once and shared across 4 rows, halving B
bandwidth vs 1-row and avoiding the extreme C write scatter of 8-row.

**Gen003 evidence (from two independent agents):**

Explore_2 (vpshufb kernel): sol04 (4-row) vs sol02 (1-row) showed:
- Medium: 530 µs vs 822 µs = **1.55x improvement**
- Large: 5682 µs vs 9470 µs = **1.67x improvement**
- Small: 13.24 µs vs 5.29 µs (4-row overhead hurts small)

Explore_1: sol02 (8-row) vs sol01 (1-row) showed:
- Large: 3213 µs vs 5349 µs = **1.67x improvement** (same factor!)
- Medium: 283 µs vs 366 µs = 1.29x improvement

**Key insight from explore_2:** "the 4-row benefit is real — ~1.6x medium/large
improvement just from B-load amortization. This is a large, reliable effect."

**Why 4-row over 8-row:**
- 4 rows × 256 KB stride (large) = 1 MB between extremes, vs 2 MB for 8-row
- Fewer live accumulator registers (4 vs 8), less compiler pressure
- Still halves B loads vs 1-row (good enough ROI)
- More balanced tradeoff between B reads and C write locality

**Not yet tested with ternlogd+popcnt kernel.** Explore_2 estimated that applying
4-row to the current best kernel could yield ~80-95 µs. This needs immediate
empirical validation in gen004.
