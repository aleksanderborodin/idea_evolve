---
id: idea_007
type: idea
name: "SIMD Packing"
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

Current pack_A and pack_B are scalar byte-by-byte loops. Use SIMD loads/stores
for the copy. For pack_B with AVX-512: load 64 bytes from B with `_mm512_loadu_si512`,
store directly to B_packed.
