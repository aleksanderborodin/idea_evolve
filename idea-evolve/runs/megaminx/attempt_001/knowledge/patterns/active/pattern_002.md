---
type: pattern
id: pattern_002
name: Greedy cancellation is sufficient — iterative deepening yields no additional gains
lifecycle: active
confidence: 0.9
first_seen: gen_001
last_updated: gen_001
evidence: [gen001_explore_2_sol01, gen001_explore_2_sol02, gen001_explore_2_sol03]
related_ideas: [idea_001]
tags: [compression, cancellation, diminishing_returns]
---

# Greedy Cancellation Is Sufficient — Iterative Deepening Yields No Additional Gains

## Observation

explore_2 compared three cancellation strategies:
1. Greedy left-to-right single pass: 46312
2. Iterative bidirectional cancellation: 46312 (no improvement)
3. Midpoint repair with random bridges: 46312 (no improvement)

The greedy single-pass cancellation already finds all adjacent X.-X pairs. Additional passes or more sophisticated cancellation strategies find nothing further.

## Implication

The residual path length after greedy cancellation represents genuine information in the random walk — not cancellation artifacts. Further compression requires either search-based path-finding or valid algebraic identities, not more aggressive cancellation.

The headroom above compression (46312 vs target 15000) is ~31k proxy moves that cannot be found by cancellation alone.