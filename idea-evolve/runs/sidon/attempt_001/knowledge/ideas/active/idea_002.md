---
id: idea_002
type: idea
name: "Local Search (Swap Neighborhood)"
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

Start from a greedy Sidon set. Define neighborhood: remove one element, try
adding a different one. Accept if the set grows or stays same size with more
room for future additions. Iterate until no improvement. Can be combined with
simulated annealing to escape local optima.
