---
id: fact_002
type: fact
name: "Cache Hierarchy"
confidence: 0.8
first_seen: generation_0
verified: false
source: user-provided
tags: []
---

- L1 Data: 48 KB per core, 12-way associative, 64-byte lines, 5-cycle latency
- L1 Instruction: 32 KB per core
- L2 Unified: 1.25 MB per core, 10-way, 64-byte lines, ~12-cycle latency
- L3 Shared: 8 MB, ~40-cycle latency
- Memory bandwidth: ~38 GB/s (dual-channel LPDDR4x-4266)
