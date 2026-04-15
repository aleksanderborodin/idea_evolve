---
type: cluster
id: cluster_001
name: "Algebraic Approaches"
lifecycle: established
confidence: 0.9
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
members: [idea_001, idea_002, idea_003, idea_011]
best_score: 616
tags: [algebraic, orbit-clique, AGL, group-theory]
---

# Cluster: Algebraic Approaches

## Description

Construction methods using group theory (orbit decompositions) to reduce the search space before clique search. All approaches rely on `helpers/agl18.py`.

## Evidence

- AGL(1,8) orbit clique: 6 solutions → 616 (optimal for AGL)
- Individual extension attempts: 2 solutions → 0 extensions (orbit-closed)
- Multi-seed verification: 1 solution → confirms 11-orbit maximum

## Membership

- idea_001: AGL(1,8) orbit clique (established, confidence 0.95)
- idea_002: Degree-ordered greedy clique selection (established, confidence 0.9)
- idea_003: Individual permutation extension (established, confidence 0.9)
- idea_011: Multi-seed clique search (established, confidence 0.9)

## Performance

Best score: **616** (AGL orbit clique). All member ideas converge to this result or help verify it.

## Exhausted?

**Yes for AGL alone.** Multi-seed search (500 orderings, all 720 starting vertices) confirms 11 is the maximum AGL orbit clique. No extension exists. The direction is exhausted within the AGL framework.

## For Gen 2

PGL(2,7) and PSL(2,7) belong in a new "Alternative Group Actions" cluster (not yet created). Cross-group search also belongs there.
