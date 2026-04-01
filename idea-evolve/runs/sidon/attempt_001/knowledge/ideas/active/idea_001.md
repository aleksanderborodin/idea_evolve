---
id: idea_001
type: idea
name: "Randomized Greedy with Restarts"
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

The basic greedy algorithm always adds the smallest valid element, giving 66.
Try random orderings of candidates: shuffle the range [0, 10000] and greedily
add elements that don't violate the Sidon property. Run many restarts and keep
the best. Different random orderings explore different parts of the search space.
