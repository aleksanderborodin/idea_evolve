---
type: idea
id: idea_012
name: "Stack-Allocated Aligned Buffers (No malloc/TLS)"
lifecycle: active
confidence: 0.5
first_seen: generation_1
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [explore_1/sol10, gen002/explore_1/sol01]
contradicted_by: []
related_ideas: [idea_005, idea_014]
cluster: cluster_002
tags: [allocation, stack, alignment, malloc, tls]
---

Use `alignas(64)` stack-allocated arrays for packed A and B buffers instead of
`_mm_malloc` or `thread_local` storage. For our problem's small k values, the
buffers are small enough to fit on the stack.

Gen001: explore_1/sol10 used stack buffers and achieved 148.18 µs (best score).
Gen002: The row-streaming architecture (idea_014) also uses stack allocation
implicitly — all explore_1 solutions broadcast A bytes into zmm registers
directly, and explore_1/sol06 uses stack buffers for B micro-packing.

The importance of this idea has diminished with the discovery of the row-streaming
architecture (idea_014), which eliminates the need for persistent pack buffers
entirely. Stack allocation matters mainly for BLIS-style packing where buffers
are reused across the inner loop.

Still valid but less differentiated than initially thought. The main benefit
(avoiding malloc/TLS overhead) is small relative to other optimizations.
