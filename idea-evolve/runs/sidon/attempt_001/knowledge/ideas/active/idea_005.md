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
related_ideas: [idea_003, idea_016]
cluster: cluster_002
tags: [search, backtracking, pruning, exact, untested]
---

Use depth-first search with aggressive pruning: at each step, count how many candidates remain that could be added without violation. If the count drops below (target - current_size), backtrack. This prunes hopeless branches early.

Never tested. Coverage matrix confirms zero trials. For N=10000, the search space is enormous and backtracking is unlikely to reach competitive sizes (100+) in reasonable time. May be useful for small N to calibrate ILP results or validate theoretical bounds. Low priority for score maximization.
