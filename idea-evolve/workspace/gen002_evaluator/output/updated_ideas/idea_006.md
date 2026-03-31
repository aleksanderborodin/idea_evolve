---
type: idea
id: idea_006
name: "Streaming Stores for Large m"
lifecycle: active
confidence: 0.7
first_seen: generation_0
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [full_1/sol02, full_1/sol04, gen002/experimentator_1/exp1b, gen002/explore_1/sol04, gen002/explore_2/sol04]
contradicted_by: [gen002/experimentator_1/exp1b_medium]
related_ideas: [idea_010, idea_015]
cluster: cluster_002
tags: [streaming-stores, non-temporal, memory-bandwidth, large-m]
---

For large C matrices (>8 MB), use `_mm512_stream_si512` to bypass cache on stores,
eliminating RFO (read-for-ownership) overhead and cache pollution.

**Gen002 experimental data (experimentator_1):**
- Large (32 MB C): **2.3x speedup** — streaming 4226 µs vs regular 9850 µs
- Medium (4 MB C): **0.9x — WORSE** — streaming 317 µs vs regular 299 µs
- Small (128 KB C): 1.1x — negligible

The medium regression is now explained: 4 MB fits in L3 (8 MB), and streaming
stores bypass useful cache. Streaming stores should ONLY be used when C exceeds
L3 capacity.

**CRITICAL DISCOVERY (gen002):** The benchmark harness allocates C with
`std::vector<int>`, which is NOT 64-byte aligned. `_mm512_stream_si512` requires
64-byte aligned addresses. This blocks direct streaming stores unless:
1. Runtime alignment check succeeds (depends on allocator)
2. Solution allocates an internal aligned buffer and copies back

Confidence raised from 0.5 to 0.7 based on experimentator_1's controlled
measurements. The 2.3x improvement on large is now quantified and reproducible.
Combined with the size-adaptive approach (idea_015), this is the single highest-
leverage optimization remaining.

Measured DRAM write bandwidth: 24.84 GB/s (streaming) vs 11.38 GB/s (regular)
at 32 MB — streaming stores more than double effective write bandwidth.
