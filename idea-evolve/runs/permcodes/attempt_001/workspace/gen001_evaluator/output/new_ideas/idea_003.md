---
type: idea
id: idea_003
name: "Iterated Local Search (ILS)"
lifecycle: active
confidence: 0.5
first_seen: gen001
last_updated: gen001
last_confirmed_gen: null
supported_by: []
contradicted_by: []
related_ideas: [idea_002, idea_005]
cluster: search_heuristics
tags: [iterative, local-search, perturbation, destruction-reconstruction]
---

ILS is a metaheuristic that escapes local optima by applying controlled perturbations ("destructions") to a solution, then reconstructing it via local search. For permutation codes, a destruction might remove k random codewords and then greedily rebuild.

Key questions: (1) Can ILS escape the AGL(1,8) local maximum of 616? (2) What destruction size k is optimal? (3) Does the 616-code plateau under all reasonable perturbations?

The architect assigned explore_1 to ILS in gen001 but no solution was submitted. This idea remains unvalidated.
