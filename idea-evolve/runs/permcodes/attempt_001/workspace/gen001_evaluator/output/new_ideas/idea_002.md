---
type: idea
id: idea_002
name: "AGL(1,8) Algebraic Group Construction"
lifecycle: active
confidence: 0.8
first_seen: gen001
last_updated: gen001
last_confirmed_gen: null
supported_by: [architect_report_gen001]
contradicted_by: []
related_ideas: [idea_001, idea_004]
cluster: algebraic_construction
tags: [algebraic, group-theory, agl18, maximum-clique]
---

AGL(1,8) is the affine general linear group on GF(8). It acts transitively on {0,...,7} and has 168 elements in its orbit per starting permutation. The full group has 240 orbits. Maximum clique search on the orbit graph (rather than individual permutations) yields the Smith-Montemanni bound of 616.

Implementation: `helpers.agl18.max_clique_code()` builds the orbit graph and finds the largest set of mutually compatible orbits. Each orbit contributes 168 permutations (or fewer if orbits overlap). The 616-code uses 11 orbits (11 × 56 = 616 — orbit size is actually 56, not 168 as initially thought).

This is the gold-standard reference construction that should achieve 616+. Expected to be the best single-method result.
