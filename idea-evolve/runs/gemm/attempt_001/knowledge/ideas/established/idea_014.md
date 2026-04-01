---
type: idea
id: idea_014
name: "Row-Streaming No-Pack Architecture"
lifecycle: established
confidence: 0.85
first_seen: generation_2
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen002/explore_1/sol01, gen002/explore_1/sol03, gen002/explore_1/sol05, gen002/explore_1/sol06, gen003/exploit_1/sol02, gen003/explore_1/sol01, gen003/explore_1/sol02, gen003/explore_1/sol03, gen003/explore_1/sol04]
contradicted_by: []
related_ideas: [idea_001, idea_013, idea_010]
cluster: cluster_003
tags: [no-pack, row-streaming, architecture, established]
---

Process rows of A sequentially, sweeping across all m columns of B in 64-byte
chunks. No BLIS packing, no tiling buffers. For each row i, broadcast all
k_bytes of pos/neg A bytes into zmm registers, then iterate j from 0 to m in
steps of 64, accumulating int8 diffs and widening to int32 at the end.

**Promoted to ESTABLISHED in gen003.** The row-streaming architecture has now
produced the best solution for two consecutive generations:
- Gen002: explore_1/sol01, 147.26 µs
- Gen003: exploit_1/sol02, **141.0 µs** (new overall best)

Gen003 also produced 4 more row-streaming solutions (explore_1: sol01-sol04),
confirming the architecture's robustness. All gen003 solutions scoring under
250 µs use row-streaming.

**Key gen003 finding:** The architecture is now confirmed as memory-bandwidth-bound,
not compute-bound. Multiple agents (exploit_1, explore_1, experimentator_1)
independently concluded that kernel compute optimizations yield negligible benefit
because DRAM bandwidth for C writes and B reads is the bottleneck.

**Variant performance in gen003:**
- 1-row (exploit_1/sol02): **141.0 µs** — best, with runtime NT alignment check
- 1-row (explore_1/sol01): 220 µs — baseline reimplementation
- 8-row (explore_1/sol02): 168 µs — B-load amortization helps large, C scatter hurts
- 1-row + NT (explore_1/sol04): 185 µs — NT stores don't help sequential writes

The architecture's simplicity (no pack_A, pack_B, or tiling loops) is a key strength.
The compiler produces near-optimal code for the monolithic single-function version.
