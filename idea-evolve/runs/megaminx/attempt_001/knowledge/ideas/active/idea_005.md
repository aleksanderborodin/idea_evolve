---
type: idea
id: idea_005
name: Megaminx commutator and identity discovery
lifecycle: active
confidence: 0.3
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: []
contradicted_by: []
related_ideas: [idea_002, idea_001]
cluster: compression
tags: [algebra, identities, commutators, group_theory]
---

# Megaminx Commutator and Identity Discovery

## Concept

Systematically discover valid move-sequence identities specific to Megaminx's Cayley graph. Unlike Rubik's cube where many commutator identities hold, Megaminx's 12-face geometry may have different valid transformations.

## What Happened in Gen 1

gen_001 explore_2 tried a commutator heuristic (X.Y.-X ≈ Y) that FAILED — but this was idea_002 (X.Y.-X commutator heuristic), not idea_005. The idea_002 failure does NOT contradict idea_005's approach, because idea_005 is about discovering NEW identities, not applying existing Rubik's cube identities.

**Correction made:** The previous `contradicted_by: [gen001_explore_2_sol04]` was incorrect. sol04 tested idea_002, not idea_005.

## Approach

1. Generate random paths of length 3-8 moves
2. Apply candidate transformation (e.g., A.B.A^{-1}.B^{-1})
3. Check if result equals identity or known state
4. Classify found identities by type (commutator, conjugate, etc.)
5. Use valid identities to compress sample_submission paths

## Priority

Medium. Search space is large. Even a few valid identities could unlock meaningful compression for the very_hard bucket where other approaches fail.

## Caveat

Every candidate identity must be verified mathematically on small examples before production use. The X.Y.-X failure (idea_002) is a reminder: intuition from Rubik's cube does not transfer directly.