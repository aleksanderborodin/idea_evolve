---
type: idea
id: idea_004
name: Meet-in-the-middle BFS
lifecycle: active
confidence: 0.5
first_seen: gen_001
last_updated: gen_003
last_confirmed_gen: gen_001
supported_by: [gen001_explore_1_sol01]
contradicted_by: []
related_ideas: [idea_003, idea_005, idea_012]
cluster: search_algorithms
tags: [MITM, BFS, optimal, search]
---

# Meet-in-the-Middle BFS

## Concept

Run BFS simultaneously from initial state and solved state. When frontiers intersect, concatenate forward and backward paths. Reduces depth-D problem from O(24^D) to O(2 × 24^(D/2)) states.

## Evidence from Gen 1

explore_1 implemented MITM with max_depth=6 per side (total depth 12) and confirmed it is tractable for shallow puzzles. However, for medium/hard buckets (depth 26-100+), the branching factor 24 makes even D=6 per side produce millions of states.

## Superseded by idea_012

**CayleyPy has built-in MITM+beam search via `bfs_result_for_mitm` (idea_012).** This provides the same bidirectional search benefit integrated into beam search, with automatic path concatenation. idea_012 is strictly more practical than implementing MITM manually. idea_004 is retained for its documentation of the MITM concept and depth limitations.

## Limitations

- Branching factor 24 is too large for deep searches
- BFS to depth 7 = ~4 billion forward states
- For depth > 12 total, MITM is infeasible without heavy pruning
- idea_012's MITM backstop (depth 6) helps but only saves 6 beam search steps

## When It Helps

Best for shallow puzzles (depth ≤ 20) where combined search depth may achieve optimal solutions. For very_hard bucket (depth 500-1000), MITM contribution is small relative to total depth.
