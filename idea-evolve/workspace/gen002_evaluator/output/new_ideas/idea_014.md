---
type: idea
id: idea_014
name: "Row-Streaming No-Pack Architecture"
lifecycle: active
confidence: 0.6
first_seen: generation_2
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002/explore_1/sol01, gen002/explore_1/sol03, gen002/explore_1/sol05, gen002/explore_1/sol06]
contradicted_by: []
related_ideas: [idea_001, idea_013, idea_010]
cluster: cluster_003
tags: [no-pack, row-streaming, architecture, alternative]
---

Process rows of A sequentially, sweeping across all m columns of B in 64-byte
chunks. No BLIS packing, no tiling buffers. For each row i, broadcast all
k_bytes of pos/neg A bytes into zmm registers, then iterate j from 0 to m in
steps of 64, accumulating int8 diffs and widening to int32 at the end.

This is a fundamentally different architecture from the BLIS-based approach
(idea_001 + idea_007). It eliminates pack_A and pack_B overhead entirely. The
tradeoff: B is read from its original layout (stride-m access per k-row), not
from a packed L1-resident buffer.

Gen002 evidence: explore_1 produced 8 solutions using this architecture.
Best result: sol01 at **147.26 µs** (small=3.69, med=225.55, large=3841.72),
which matches the previous gen001 BLIS best of 148.18 µs. Several variants
achieved strong small-benchmark performance (sol05: 3.37 µs, sol01: 3.69 µs)
due to zero packing overhead.

The architecture is especially competitive for small/medium where B fits in
L1/L2 anyway. For large, it trails BLIS slightly because B (448 KB) doesn't
stay L1-resident across all rows. However, explore_1/sol06 introduced a
hybrid: B micro-packing per 64-col chunk for large k_bytes (see idea_017),
which helped large significantly.

Key variants tested:
- 1-row processing (sol01): simple, 147.26 µs
- 2-row with inline A (sol03): 175.65 µs — less good than 1-row
- 2-row + streaming stores (sol04): 195.22 µs — streaming store overhead
- 2-row + B micro-pack for large (sol06): 177.02 µs
- NC=256 panel pack for medium (sol08): 180.07 µs

The 1-row variant was surprisingly the best, likely because it maximizes
B-data reuse within each row sweep before moving to the next row.
