---
id: idea_009
type: idea
name: "Wider Micro-Kernel 8x64"
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

With 32 zmm registers (AVX-512), we can afford 8 rows × 1 zmm accumulator per row
= 8 registers for accumulators, plus a few for B data and temporaries. Process 8
rows of A at once instead of 4, halving the number of micro-kernel calls.
