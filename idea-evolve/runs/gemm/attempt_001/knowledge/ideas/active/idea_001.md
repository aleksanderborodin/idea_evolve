---
id: idea_001
type: idea
name: "AVX-512 Micro-Kernel with Hardware Popcount"
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

Replace the 6-instruction LUT-based popcount (`vpshufb` + masks) with a single
`_mm512_popcnt_epi8()` instruction (AVX512_BITALG). Process 64 bytes of B per
iteration instead of 32 (AVX2). Micro-kernel shape becomes 4x64 (4 rows of A,
64 columns of B). This alone could give ~1.5-2x speedup in the micro-kernel.
