---
type: idea
id: idea_009
name: "Wider Micro-Kernel 8x64"
lifecycle: disputed
confidence: 0.4
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: []
contradicted_by: [explore_1/sol03]
related_ideas: [idea_001, idea_004]
cluster: cluster_001
tags: [micro-kernel, 8x64, register-pressure, avx512]
---

With 32 zmm registers (AVX-512), we can afford 8 rows × accumulators. Process 8
rows of A at once instead of 4, halving the number of micro-kernel calls.

explore_1/sol03 attempted an 8-row × 64-col micro-kernel and got 493.42 µs —
worse than the 4×64 sol02 (400.68 µs). The agent reported "register pressure
hurt it." With 8 rows of int16 accumulators (2 zmm each = 16 zmm) plus B data,
broadcast registers, and temporaries, register pressure forces spills to memory.

No solution in gen001 successfully improved performance with an 8-row kernel.
The 4-row kernel is consistently the best shape. However, the 8-row kernel has
not been tested with int8 accumulation (which uses 1 zmm per row instead of 2),
so the register budget might work with that approach.

Disputed: theoretically sound but practically failed in gen001. Needs further
experimentation with lighter accumulation strategies.
