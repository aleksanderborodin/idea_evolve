---
id: fact_004
type: fact
name: "Key Instruction Latencies"
confidence: 0.8
first_seen: generation_0
verified: false
source: user-provided
tags: []
---

- `vpopcntb` (zmm, BITALG): port 5, 1c latency, 1c throughput — per-byte popcount
- `vpdpbusd` (zmm, VNNI): port 0, 5c latency, 1c throughput — int8 dot-product
- `vpshufb` (ymm/zmm): port 5, 1c latency, 1c throughput
- `vpandd`/`vpord`/`vpxord` (zmm): port 0 or 5, 1c latency, 0.5c throughput (2 per cycle)
- `vpmovzxbd` / `vpmovsxbd` (zmm): port 5, 3c latency, 1c throughput — widen 8→32
- `_mm512_set1_epi8`: 1c throughput via broadcast
