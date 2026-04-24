---
type: idea
id: idea_012
name: CayleyPy built-in MITM+beam search via bfs_result_for_mitm
lifecycle: active
confidence: 0.9
first_seen: gen_003
last_updated: gen_004
last_confirmed_gen: gen_004
supported_by: [gen003_research_1, gen004_exploit_1_sol01]
contradicted_by: []
related_ideas: [idea_004, idea_003, idea_008]
cluster: search_algorithms
tags: [MITM, beam_search, cayleypy, BFS, backstop, built_in]
---

# CayleyPy Built-In MITM+Beam Search via bfs_result_for_mitm

## Summary

CayleyPy's `beam_search` method accepts a `bfs_result_for_mitm` parameter that enables
meet-in-the-middle search automatically. When provided, beam search terminates not only
on the exact central state, but on any state in the precomputed BFS neighborhood. The
path length is `beam_depth + bfs_layer_depth`, effectively halving the required search depth.

## Evidence

research_1 (gen003) verified this works on sid=10 (depth 10):
- Without MITM: beam search finds path of length 12
- With MITM (bfs_result depth 6): beam search finds optimal path of length 10

exploit_1 (gen004) used MITM in the combined recipe pipeline:
- BFS depth 6 computed in ~2s, used as MITM backstop
- Integrated correctly with beam search (beam_width=4096)
- Overall pipeline scored 44111 (marginal improvement due to training data depth, not MITM)

## Critical Implementation Detail

The BFS result and beam search MUST use the **same CayleyGraph instance**. The StateHasher
uses random seeds, so BFS computed on one graph instance cannot be used with beam search
on a different instance — hash values mismatch and the intersection check silently fails.

## Mutual Exclusivity with Non-Backtracking

**Non-backtracking beam search (`beam_mode='advanced'`, idea_015) is INCOMPATIBLE with
`bfs_result_for_mitm`.** Agents must choose: MITM backstop (this idea) OR non-backtracking
(idea_015), not both. For very_hard puzzles (depth 500-1000), non-backtracking may provide
more benefit than MITM's 6-step savings. Head-to-head comparison needed.

## Integration with idea_010

The BFS result used for MITM is the SAME computation used for training data (idea_010).
One BFS call produces both:
1. MITM backstop for beam search (primary value)
2. Exact-distance training data for shallow states (supplementary)

## Impact on Score

The MITM backstop is most valuable for short/medium puzzles (depth ≤ 50) where beam search
can reach the MITM intersection. For very_hard puzzles (depth 500–1000), the 6-step MITM
reduction is small relative to the total depth, but every saved step counts.
