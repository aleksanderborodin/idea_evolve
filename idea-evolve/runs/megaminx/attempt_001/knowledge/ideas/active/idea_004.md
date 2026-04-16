---
type: idea
id: idea_004
name: Meet-in-the-middle BFS
lifecycle: active
confidence: 0.5
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: [gen001_explore_1_sol01]
contradicted_by: []
related_ideas: [idea_003, idea_005]
cluster: search_algorithms
tags: [MITM, BFS, optimal, search]
---

# Meet-in-the-Middle BFS

## Concept

Run BFS simultaneously from initial state and solved state. When frontiers intersect, concatenate forward and backward paths. Reduces depth-D problem from O(24^D) to O(2 × 24^(D/2)) states.

## Evidence from Gen 1

explore_1 implemented MITM with max_depth=6 per side (total depth 12) and confirmed it is tractable for shallow puzzles. However, for medium/hard buckets (depth 26-100+), the branching factor 24 makes even D=6 per side produce millions of states. MITM only helps when the optimal distance is ≤ 2 × max_depth_per_side.

The special bucket (id=0, depth=72) is theoretically tractable with MITM depth 36 per side, but explore_1 used max_depth=6 and still found no improvement over cancellation.

## Limitations

- Branching factor 24 is too large for deep searches
- BFS to depth 7 = ~4 billion forward states, ~8 billion total with backward
- For depth > 12 total, MITM is infeasible without heavy pruning
- MITM provides optimal solutions but only for shallow puzzles

## When It Helps

Best for medium bucket (depth 26-100) where combined search depth 20-40 may be achievable. For very_hard bucket (depth 500-1000), even meeting at depth 250+ is intractable.

## Relationship to Predictor

MITM and predictor-guided beam search are complementary. MITM guarantees optimal solutions for shallow puzzles; predictor-guided beam handles deep puzzles approximately.