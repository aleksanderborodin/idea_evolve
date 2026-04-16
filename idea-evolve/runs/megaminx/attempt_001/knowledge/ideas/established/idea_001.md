---
type: idea
id: idea_001
name: Basic move cancellation compression
lifecycle: established
confidence: 0.95
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: [gen001_explore_1_sol01, gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04, gen001_explore_1_sol05, gen001_explore_2_sol01, gen001_explore_2_sol02, gen001_explore_2_sol03, gen001_explore_2_sol05, gen001_full_1_sol01]
contradicted_by: []
related_ideas: [idea_002, idea_003]
cluster: compression
tags: [compression, baseline, cancellation]
---

# Basic Move Cancellation Compression

## Summary

Sample submission paths are exact inverses of random walks used to scramble puzzles. Random walks contain internal X.-X cancellations (adjacent inverse move pairs) that make paths longer than necessary. By iteratively removing adjacent inverse pairs, paths can be shortened by 8-15% with zero search cost.

## How It Works

The algorithm is simple: iterate through moves, and whenever an adjacent pair m followed by its inverse -m (or vice versa) is found, remove both. Repeat until no more cancellations exist.

Implementation: greedy left-to-right pass, repeated until fixed point. All 5 explore_1 solutions, 4 explore_2 solutions, and full_1 all converged on this same approach independently.

## Evidence

All 11 evaluated solutions use cancellation as a baseline. Achieved compression_ratio of 0.9158 across all solutions, corresponding to 8.4% improvement over sample_submission (50572 → 46312). This is at the lower end of the predicted 5-15% range from initial_ideas.md.

## When It Helps

Always useful as a baseline — it costs nothing and always preserves validity. Apply to sample_submission paths before any other optimization. The remaining headroom after greedy cancellation is the actual problem.

## Limitations

Greedy adjacent cancellation only catches immediate inverses. Longer-range cancellations (e.g., X.Y.-X.-Y patterns, or X.Y.Z.-Y.-Z.-X) survive this pass. Iterative deepening beyond 1-2 extra passes shows diminishing returns — explore_2's iterative bidirectional cancellation found no additional gains over the greedy single-pass.

## Current Best Score

fitness=46312, compression_ratio=0.9158, improved_count=98/101 puzzles.