---
type: pattern
id: pattern_004
name: "Direct greedy needs orbit structure"
lifecycle: active
confidence: 0.9
first_seen: gen_01
last_updated: gen_01
evidence: [gen001_explore_1_sol04, gen001_explore_2_sol01]
related_ideas: [idea_005, idea_002]
tags: [greedy, orbit, structure, baseline]
---

# Direct Greedy Needs Orbit Structure

## Pattern Description

Greedy construction on the full 40320-permutation graph gets trapped at ~262 codewords (43% of optimum). The same greedy algorithm on the 720-vertex AGL orbit graph reaches 616. The 354-codeword difference is entirely due to the orbit decomposition.

## Evidence

- Direct greedy on 40320 vertices: 262 (explore_1/sol04)
- Greedy on 720 AGL orbits (each orbit = 56 equivalent permutations): 616
- ILNS (greedy + neighborhood search): 290-293 (only ~28 more than pure greedy)

## Implications

The orbit decomposition is not just a speedup — it fundamentally changes which solutions are reachable by greedy. Without algebraic structure, the greedy algorithm gets lost in a vast space of equivalent permutations.
