---
type: idea
id: idea_010
name: "Skip memset — Direct Store Without Pre-Zeroing C"
lifecycle: established
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol04]
contradicted_by: []
related_ideas: [idea_006, idea_008]
cluster: cluster_002
tags: [memset, direct-store, memory-bandwidth, zero-elimination]
---

When k_bytes ≤ 7 and m%64==0 and n%4==0 (true for all benchmark sizes), each C
element is written exactly once by the micro-kernel (no KC tiling means no
accumulation across tiles). Direct stores overwrite C completely, so `memset(C, 0, ...)`
is pure wasted bandwidth.

This was the single largest optimization discovered in gen001. The savings are
enormous for the large benchmark:
- Large (C = 128×65536×4 = 32 MB): memset costs ~1066 µs at ~30 GB/s bandwidth
- Medium (C = 64×16384×4 = 4 MB): memset costs ~40 µs
- Small (C = 32×1024×4 = 128 KB): memset costs ~0.6 µs

Evidence: explore_1/sol08 removed memset and jumped from 306.60 µs (sol07) to
178.28 µs — a **1.72x speedup** from this single change. full_1/sol04 also
skips memset conditionally and achieves 167.23 µs (4.61x vs baseline).

Both agents independently noted this as their most surprising finding. Explore_1
reported: "memset was costing ~3.5 ms on large — nearly half the total time!"

The approach requires a correctness fallback: if dimensions are not aligned to
micro-kernel tile sizes, or k_bytes > 7 (int8 overflow risk), memset must still
be used. All implementations include this safety check.
