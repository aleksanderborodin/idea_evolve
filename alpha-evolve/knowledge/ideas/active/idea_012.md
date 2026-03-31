---
type: idea
id: idea_012
name: "Stack-Allocated Aligned Buffers (No malloc/TLS)"
lifecycle: active
confidence: 0.5
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol10]
contradicted_by: []
related_ideas: [idea_005]
cluster: cluster_002
tags: [allocation, stack, alignment, malloc, tls]
---

Use `alignas(64)` stack-allocated arrays for packed A and B buffers instead of
`_mm_malloc` or `thread_local` storage. For our problem's small k values, the
buffers are small enough to fit on the stack:
- A_packed: MC/4 × MAX_KB × 8 = 16 × 32 × 8 = 4096 bytes
- B_packed: NC/64 × MAX_KB × 64 = 4 × 32 × 64 = 8192 bytes

explore_1/sol10 used stack buffers and achieved 148.18 µs (best score), versus
sol09's 171.04 µs with thread_local buffers. The improvement is modest (~13%)
but consistent. Stack allocation avoids:
- `_mm_malloc`/`_mm_free` overhead per call (full_1/sol04 uses _mm_malloc)
- TLS indirection overhead (sol09's thread_local approach hurt small benchmark)
- Potential allocator contention in multi-threaded scenarios

The main limitation is stack size: 4096 + 8192 = 12 KB is fine, but larger NC
or MC values would exceed safe stack limits. This approach is specific to our
small k problem.
