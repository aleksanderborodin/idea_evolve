---
id: idea_002
type: idea
name: "Fully Unrolled k-Loop"
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

k_bytes is always 2, 4, or 7 for our benchmark sizes. Instead of a generic loop,
create specialized versions for each k value. With k=2, the entire inner product
is just 2 iterations — the loop overhead dominates. Template specialization or
`switch(k_bytes)` dispatch to hand-unrolled code.
