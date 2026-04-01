---
id: idea_005
type: idea
name: "Backtracking with Pruning"
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

Use depth-first search with aggressive pruning: at each step, count how many
candidates remain that could be added without violation. If the count drops
below (target - current_size), backtrack. This prunes hopeless branches early.
