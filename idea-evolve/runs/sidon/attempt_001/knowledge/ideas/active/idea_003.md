---
id: idea_003
type: idea
name: "Difference-Aware Construction"
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

Instead of checking violations after the fact, maintain the set of used differences
explicitly. When choosing the next element to add, pick one that uses "rare"
differences (large gaps in the difference spectrum). This leaves more room for
future elements.
