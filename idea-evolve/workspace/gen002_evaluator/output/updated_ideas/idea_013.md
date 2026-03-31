---
type: idea
id: idea_013
name: "No-Packing Direct Kernel"
lifecycle: disputed
confidence: 0.3
first_seen: generation_1
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002/explore_2/sol04]
contradicted_by: [gen002/explore_2/sol01, gen002/explore_2/sol02, gen002/explore_2/sol03]
related_ideas: [idea_007, idea_005, idea_014]
cluster: cluster_002
tags: [packing, direct-access, no-pack, cache]
---

Skip B packing entirely and read B directly from its original layout. For small
benchmark (k_bytes=2, B = 2 KB), B fits entirely in L1. For medium (k_bytes=4,
B = 64 KB), B fits in L2. For large (k_bytes=7, B = 448 KB), B fits in L2.

**Gen002 testing (explore_2):** Four solutions tested this approach with varying
loop orders and register strategies:
- sol01 (jc-outer, 8-row): 207.32 µs — B loaded once per 64-col block, C writes scattered
- sol02 (template+always_inline): 318.96 µs — I-cache bloat from 3 inlined switch branches
- sol03 (named vars, fast path): 200.38 µs — best register allocation variant
- sol04 (ic-outer, jc-inner): 182.31 µs — sequential C writes, but B re-read n/4 times

Best no-pack result: 182.31 µs vs BLIS best 148.18 µs — **23% worse overall**.

Explore_2's key finding: packing cost is negligible (~2 µs), but L1-speed access
to packed B in the micro-kernel dominates. The no-pack approach suffers from L2
latency on B reads, especially for large.

However, sol04 achieved the best small-benchmark time across ALL gen002 solutions:
**3.66 µs** (vs 3.37 µs from explore_1's no-pack row-streaming). For small, where
B (2 KB) fits in L1 anyway, packing overhead is wasted.

Moved to **disputed**: the idea is wrong for large but partially valid for small
where B naturally fits in L1. A hybrid approach (no-pack for small, BLIS for
large) could combine the benefits.
