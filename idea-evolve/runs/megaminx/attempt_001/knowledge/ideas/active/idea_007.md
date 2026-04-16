---
type: idea
id: idea_007
name: Corner-only pattern database for IDA*
lifecycle: active
confidence: 0.4
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: []
contradicted_by: []
related_ideas: [idea_004, idea_003]
cluster: heuristics
tags: [pattern_database, IDA_star, admissible_heuristic]
---

# Corner-Only Pattern Database for IDA*

## Concept

Precompute exact distances for corner-only Megaminx configurations. The corner-only state space (20 corners, orientations) is small enough to enumerate exhaustively. Use the precomputed distance as an admissible heuristic for IDA* search on the full puzzle.

## Rationale

IDA* with a strong admissible heuristic can solve puzzles optimally with depth-first memory requirements. If the corner-only pattern database is accurate enough, it could find optimal paths for medium and even hard buckets.

## Challenges

- Megaminx has 20 corners with orientations. The enumeration size needs to be verified as tractable.
- Corner-only distance may be a weak heuristic for the full puzzle (corners don't capture all constraints).
- Implementation complexity: need to project full state to corner-only representation and look up distance.

## Status

Hypothesized in initial_ideas.md, confirmed as a reasonable direction but not attempted in gen_1. Medium priority — less immediately actionable than predictor training but potentially more rigorous (optimal solutions vs approximate).