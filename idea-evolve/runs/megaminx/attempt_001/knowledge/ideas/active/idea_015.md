---
type: idea
id: idea_015
name: Non-backtracking beam search (advanced beam mode)
lifecycle: active
confidence: 0.6
first_seen: gen_004
last_updated: gen_004
last_confirmed_gen: gen_004
supported_by: [gen004_research_1]
contradicted_by: []
related_ideas: [idea_003, idea_012]
cluster: search_algorithms
tags: [beam_search, non_backtracking, advanced_mode, cayleypy]
---

# Non-Backtracking Beam Search (Advanced Beam Mode)

## Summary

CayleyPy's `beam_search` has an "advanced" mode that implements non-backtracking: the beam
never revisits a state that was already explored. The CayleyPy-1 paper (arXiv:2502.13266)
shows this quadruples success rate from 17.6% to 69.7% for the same beam width on LRX graphs.
**This is a free performance boost that we have not tried.** Requires a trained predictor
(returns path=None without one).

## Confidence Note

Confidence reduced from 0.8 to 0.6 by consistency reviewer gen004. The 4x success rate
improvement is from the CayleyPy paper on LRX-16 graphs, not Megaminx. The actual benefit
on Megaminx's 24-generator Cayley graph with depth 500-1000 puzzles is unknown until tested.
The theoretical argument is strong (pruning redundant exploration always helps) but the
magnitude is uncertain.

## Critical Implementation Notes

1. Advanced mode requires a trained predictor. Without one, it returns `path=None`.
2. Advanced mode is INCOMPATIBLE with `bfs_result_for_mitm` (MITM). They are mutually
   exclusive. Agents must choose: MITM backstop (idea_012) OR non-backtracking (this idea).
3. For very_hard puzzles (depth 500-1000), non-backtracking likely provides MORE benefit
   than MITM's fixed 6-step savings, since it prunes the entire search tree at every step.

## Evidence

From the CayleyPy-1 paper: beam search with non-backtracking on LRX-16:
- Simple beam (beam_width=2^20): 17.6% solved
- Advanced beam (same width): 69.7% solved (4x improvement)

This is the single largest algorithmic improvement available beyond beam width scaling.

## Priority

High. This is likely more impactful than MITM backstop for hard/very_hard puzzles.
If forced to choose between MITM (idea_012) and non-backtracking, prefer non-backtracking
for very_hard puzzles. A head-to-head comparison at the same beam_width is needed.
