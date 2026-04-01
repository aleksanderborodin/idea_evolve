---
type: idea
id: idea_017
name: "B Micro-Packing per 64-Column Chunk"
lifecycle: active
confidence: 0.4
first_seen: generation_2
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002/explore_1/sol06]
contradicted_by: [gen002/explore_1/sol07]
related_ideas: [idea_007, idea_014, idea_013]
cluster: cluster_002
tags: [packing, micro-pack, B-panel, large-benchmark, cache]
---

For large benchmarks (k_bytes >= 5), pack each 64-column B chunk to an aligned
stack buffer before iterating all n rows. This converts ~28 MB of repeated L2
reads into one 448 KB L2 read + L1 reuse across all rows.

Explore_1/sol06 introduced this technique within the row-streaming architecture.
The large benchmark improved 46% when B micro-packing was applied (6914 µs →
3900 µs according to the agent's measurements).

However, applying the same technique to medium REGRESSED performance:
- sol07 applied micro-pack to medium: 4571 µs large vs sol06's 3900 µs — worse
- The regression is caused by non-sequential C row writes when iterating by
  B panel. C rows are spaced 64 KB apart for medium (m=16384), overwhelming
  write-combining buffers.

The key constraint: B micro-packing changes the loop order to j-outer (B panel),
i-inner (rows), which disrupts sequential C writes. This is beneficial for large
(where B reuse across rows saves L2 bandwidth) but harmful for medium (where
scattered C writes cost more than repeated B reads).

This technique is essentially a lightweight version of BLIS pack_B, applied
selectively. It suggests that the optimal approach may be a hybrid: no packing
for small/medium (B fits in L1/L2), micro-packing for large.
