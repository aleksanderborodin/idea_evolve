---
type: idea
id: idea_006
name: "Streaming Stores for Large m"
lifecycle: active
confidence: 0.5
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [full_1/sol02, full_1/sol04]
contradicted_by: []
related_ideas: [idea_010]
cluster: cluster_002
tags: [streaming-stores, non-temporal, memory-bandwidth, large-m]
---

For m=65536, each output row is 256KB — doesn't fit in L2. Use `_mm512_stream_si512`
to bypass cache on stores, freeing cache capacity for B data.

full_1/sol02 used streaming NT stores when C is 64-byte aligned and m >= 16384.
Score: 339.09 µs. However, the benefit is hard to isolate because sol02 also
introduced int8 accumulation simultaneously. full_1/sol04 (167.23 µs) includes
streaming stores as well but the dominant improvement was memset elimination.

The research agent estimated streaming stores save ~6% on the large benchmark by
eliminating read-for-ownership overhead (Finding 6). This is a modest but real gain,
primarily relevant for the large benchmark (32 MB output).

Note: streaming stores require 64-byte aligned C pointer and `_mm_sfence()` after.
C alignment is not guaranteed by the harness — full_1/sol04 checks alignment at
runtime and falls back to regular stores if unaligned. This is the correct approach.

Needs more isolated testing to quantify the standalone impact.
