---
type: idea
id: idea_002
name: X.Y.-X commutator heuristic — INVALID for Megaminx
lifecycle: debunked
confidence: 0.9
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: []
contradicted_by: [gen001_explore_2_sol04]
related_ideas: [idea_001]
cluster: compression
tags: [compression, heuristic, debunked, commutator]
---

# X.Y.-X Commutator Heuristic — INVALID for Megaminx

## What Was Claimed

The heuristic tried: in an X.Y.-X pattern, keep only Y (treating it as approximately equivalent to a commutator-like cancellation). Rationale: in commutative groups, X.Y.X^{-1} ≈ Y.

## Why It Failed

Megaminx's Cayley graph is NOT commutative. The face turns do not commute — the order of moves fundamentally changes the outcome. Applying X.Y.-X → Y changes the final state, so the resulting path does not solve the puzzle.

explore_2/sol04 attempted this with a face-move heuristic (keep non-face moves when X is a face move) and produced an INVALID solution with fitness 50474 — worse than pure cancellation (46312). The compression_ratio of 0.9981 shows it barely compressed at all, and the final state was wrong for some puzzles.

## Lesson

Do not apply commutator identities from Rubik's-cube literature without verifying they hold for Megaminx. Megaminx's generator set has different algebraic properties. All move-sequence transformations must be verified by applying the resulting path to the initial state and checking `is_solved()`.

## Status

Debunked for Megaminx. The search space for valid Megaminx-specific identities is still open — see idea_005 (commutator discovery).