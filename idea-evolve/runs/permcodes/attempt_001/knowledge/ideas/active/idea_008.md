---
id: idea_008
type: idea
name: "Skip Tiling for Small k"
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

When k_bytes ≤ 7, the entire k-dimension fits in registers. The KC loop always
has exactly one iteration. Remove the KC-tiling overhead entirely — just iterate
over m-tiles and n-tiles directly.
