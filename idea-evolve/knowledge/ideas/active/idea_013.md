---
type: idea
id: idea_013
name: "No-Packing Direct Kernel"
lifecycle: active
confidence: 0.3
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: []
contradicted_by: []
related_ideas: [idea_007, idea_005]
cluster: cluster_002
tags: [packing, direct-access, no-pack, cache]
---

Skip B packing entirely and read B directly from its original layout. For small
benchmark (k_bytes=2, B = 2×1024 = 2 KB), B fits entirely in L1 without any
packing. For medium (k_bytes=4, B = 4×16384 = 64 KB), B fits in L2. Even for
large (k_bytes=7, B = 7×65536 = 448 KB), B fits in L2.

Since B is accessed as `B[k * m + j]`, reading 64 consecutive bytes at offset j
is a single cache line (or 2 cache lines). The stride between k-rows is m bytes,
which may cause TLB misses for large m. But with only 2-7 k-rows, this is at
most 7 TLB entries.

This idea was suggested by full_1 agent ("no-packing micro-kernel" experiment)
and research agent (Finding 5 notes B fits in L2). No solution attempted it in
gen001. The potential benefit is eliminating pack_B overhead entirely, which was
identified as a major bottleneck by explore_1 (bigger than micro-kernel itself
for medium/large).

Risk: strided access pattern may be less cache-friendly than packed sequential
access, especially for the large benchmark. Needs empirical testing.
