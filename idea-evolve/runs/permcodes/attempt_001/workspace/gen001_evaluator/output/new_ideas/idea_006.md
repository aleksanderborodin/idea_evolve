---
type: idea
id: idea_006
name: "Tabu Search for Maximum Clique"
lifecycle: active
confidence: 0.5
first_seen: gen001
last_updated: gen001
last_confirmed_gen: null
supported_by: []
contradicted_by: []
related_ideas: [idea_003, idea_005]
cluster: search_heuristics
tags: [tabu-search, maximum-clique, local-search, memory]
---

A dedicated tabu search on the full compatibility graph G(8,5) (40320 vertices) could complement orbit-based approaches. Unlike ILS which operates on the code itself, tabu search operates on the independent set problem directly.

The architect noted this was not assigned in gen001 due to wanting to see ILS results first. If ILS fails to beat 616, tabu search becomes a priority for gen002.

Risk: graph has 40320 vertices, dense connectivity. Tabu tenure and neighborhood size must be carefully tuned.
