---
id: idea_006
type: idea
name: "Streaming Stores for Large m"
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

For m=65536, each output row is 256KB — doesn't fit in L2. The output won't be
re-read soon. Use `_mm512_stream_si512` to bypass cache on stores, freeing cache
capacity for B data.
