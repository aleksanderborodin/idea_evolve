---
id: fact_005
type: fact
name: "Benchmark Sizes"
confidence: 0.8
first_seen: generation_0
verified: false
source: user-provided
tags: []
---

| Label  | n   | m      | k_bits | k_bytes | A size | B size   | C size     |
|--------|-----|--------|--------|---------|--------|----------|------------|
| Small  | 32  | 1,024  | 16     | 2       | 128B   | 2 KB     | 128 KB     |
| Medium | 64  | 16,384 | 32     | 4       | 512B   | 64 KB    | 4 MB       |
| Large  | 128 | 65,536 | 56     | 7       | 1.8 KB | 448 KB   | 32 MB      |

k_bytes is always tiny (2-7). A always fits in L1. B-panels need L2 tiling.
C is huge for large m — consider streaming stores.
