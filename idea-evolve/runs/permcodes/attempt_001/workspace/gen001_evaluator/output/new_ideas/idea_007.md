---
type: idea
id: idea_007
name: "Partial Orbit Mixing"
lifecycle: active
confidence: 0.6
first_seen: gen001
last_updated: gen001
last_confirmed_gen: null
supported_by: [architect_report_gen001]
contradicted_by: []
related_ideas: [idea_002, idea_003]
cluster: algebraic_construction
tags: [algebraic, partial-orbits, hybridization]
---

Standard AGL(1,8) construction uses complete orbits. But validity only requires pairwise distance ≥ d — no group closure property. This means we can take partial permutations from an orbit and mix them with full orbits from another group.

Concretely: k full orbits × 56 perms + m partial permutations from a (k+1)th orbit. This could exceed the 11-orbit clique limit if the partial permutations are carefully chosen.

This idea is enabled by the fact that orbits are not closed under the distance constraint — only under group action. Architect flagged this as the key unexplored direction.
