---
type: fact
id: fact_007
name: "Measured DRAM Bandwidth on Target Machine"
confidence: 0.85
first_seen: generation_2
verified: true
source: "experimentator_1 bandwidth microbenchmark (gen002)"
tags: [bandwidth, DRAM, memory, streaming, measurement]
---

Experimentator_1 (gen002) measured actual memory bandwidth on the target machine
(Intel i5-1135G7, DDR4-3200 dual-channel):

**Write Bandwidth (GB/s):**

| Size | Stream write | Regular write | memset |
|------|-------------|--------------|--------|
| 128 KB | 10.94 | 24.87 | 24.84 |
| 4 MB | 18.21 | 17.16 | 14.26 |
| 32 MB | **24.84** | 11.38 | 17.71 |
| 64 MB | 22.01 | 10.14 | 18.99 |

**Read Bandwidth:** 128KB: 47.6 GB/s, 4MB: 19.0 GB/s, 32MB: 12.9 GB/s

Key implications:
- At 32 MB (large benchmark C), streaming stores achieve 24.84 GB/s — 2.2x
  faster than regular stores (11.38 GB/s) due to RFO elimination
- At 4 MB (medium benchmark C), regular stores (17.16 GB/s) slightly beat
  streaming stores (18.21 GB/s) because data fits in L3
- The theoretical DDR4-3200 peak of 51.2 GB/s is not achieved — practical
  maximum is ~25 GB/s for streaming writes

Theoretical minimum times with streaming stores:
- Small (128 KB C): ~7.7 µs (but L1-resident, so compute-limited)
- Medium (4 MB C): ~247 µs
- Large (32 MB C): ~2054 µs
