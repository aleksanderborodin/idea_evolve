---
id: idea_005
type: idea
name: "Re-tune BLIS Tile Sizes for Tiger Lake"
lifecycle: active
confidence: 0.3
first_seen: generation_0
last_updated: generation_0
last_confirmed_gen: 0
supported_by: []
contradicted_by: []
related_ideas: []
cluster: null
tags: []
---

Current: MC=64, KC=128, NC=256 (tuned for AVX2).
Tiger Lake has L1d=48KB, L2=1.25MB. With AVX-512 (64-byte wide ops):
- NC should be larger (more columns per B-panel, amortize B-packing)
- MC could stay at 64 (L1 fits 64 × 7 × 2 = 896 bytes of packed A easily)
- KC is irrelevant since k_bytes ≤ 7 always fits
