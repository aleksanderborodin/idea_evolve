---
type: idea
id: idea_012
name: "Stack-Allocated Aligned Buffers (No malloc/TLS)"
lifecycle: active
confidence: 0.5
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [explore_1/sol10, gen002/explore_1/sol01, gen003/exploit_1/sol02]
contradicted_by: []
related_ideas: [idea_005, idea_014]
cluster: cluster_002
tags: [allocation, stack, alignment, malloc, tls]
---

Use `alignas(64)` stack-allocated arrays for packed A and B buffers instead of
`_mm_malloc` or `thread_local` storage. For our problem's small k values, the
buffers are small enough to fit on the stack.

Gen003: the new best (exploit_1/sol02, 141.0 µs) uses stack-allocated `__m512i
a_pos[32], a_neg[32]` arrays for pre-broadcast A values. This is consistent with
the pattern but the stack allocation itself is not the differentiating factor.

The importance of this idea continues to diminish with the row-streaming architecture
(idea_014), which eliminates persistent pack buffers entirely. The pre-broadcast A
arrays are small (max 7 × 64 = 448 bytes) and the compiler may place them in
registers directly.

Still valid but low-priority — a hygiene best practice rather than a performance
differentiator.
