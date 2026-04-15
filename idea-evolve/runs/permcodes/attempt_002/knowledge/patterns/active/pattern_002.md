---
type: pattern
id: pattern_002
name: "AGL 616-code is orbit-closed"
lifecycle: active
confidence: 0.9
first_seen: gen_01
last_updated: gen_01
evidence: [gen001_explore_1_sol02, gen001_full_1_sol02]
related_ideas: [idea_003]
tags: [orbit-closure, extension, maximality, AGL]
---

# AGL 616-Code is Orbit-Closed

## Pattern Description

The 616-code constructed from 11 AGL(1,8) orbits has the property that no permutation outside those 11 orbits is compatible with all 616 codewords. Two independent experiments (explore_1/sol02 and full_1/sol02) both found exactly zero compatible non-orbit permutations.

## Evidence

- **2/2 extension attempts** found 0 compatible individual permutations
- The 616-code is "maximally compatible" within the AGL structure
- This means the 616-code cannot be extended by single permutations — only by finding a fundamentally different construction

## Implications

To beat 616, one must find a different orbit decomposition (different group action) or a non-orbit-based construction. Individual extension of the AGL code is a dead end.
