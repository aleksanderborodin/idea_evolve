---
type: cluster
id: cluster_003
name: "Alternative Architectures (Non-BLIS)"
member_ideas: [idea_014]
best_score: 147.26
best_solution: gen002/explore_1/sol01
status: active
last_updated: generation_2
---

This cluster groups ideas about fundamentally different kernel architectures
that do not follow the BLIS packing/tiling template. Currently contains:
- idea_014: Row-streaming no-pack architecture

**Gen002 established this cluster.** All 14 gen001 solutions followed the BLIS
template. Gen002's explore_1 introduced a row-streaming architecture that
processes one row at a time, sweeping across all m columns with no packing.
This achieved **147.26 µs** — matching the BLIS best (148.18 µs).

The row-streaming architecture has distinct advantages:
- Zero packing overhead (BLIS pack is ~6% of total, small but nonzero)
- Simpler code (no pack_A, pack_B, or tiling loops)
- Naturally sequential C writes (enables NT stores without layout conflicts)
- Best small-benchmark performance (3.37 µs vs 4.49 µs BLIS)

And disadvantages:
- B read from original layout (stride-m) instead of packed L1-resident buffer
- Slightly worse for large where B reuse across rows matters
- Less amenable to multi-row unrolling (adding rows means more register pressure)

**Strategic significance:** This cluster represents the first architectural
diversity in the solution population. The BLIS approach hit diminishing returns
(pattern_007), so this alternative architecture opens new optimization paths.
In particular, the row-streaming architecture is naturally compatible with
size-adaptive NT stores (idea_015), which could be the key to reaching the 24 µs
target.

**Next frontier:**
- Combine row-streaming with size-adaptive NT stores
- 2-row or 4-row variants with int8 accumulation
- Hybrid: row-streaming for small/medium, BLIS for large
