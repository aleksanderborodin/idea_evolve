---
type: pattern
id: pattern_001
name: Cancellation ceiling — unguided search adds nothing
lifecycle: active
confidence: 0.95
first_seen: gen_001
last_updated: gen_001
evidence: [gen001_explore_1_sol01, gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04, gen001_explore_1_sol05, gen001_explore_2_sol01, gen001_explore_2_sol02, gen001_explore_2_sol03, gen001_explore_2_sol05, gen001_full_1_sol01]
related_ideas: [idea_001, idea_003]
tags: [beam_search, compression, ceiling]
---

# Cancellation Ceiling — Unguided Search Adds Nothing

## Observation

All solutions that used unguided beam search (cayleypy_beam_solver without a predictor) converged to exactly the same fitness as pure cancellation: 46312. Beam widths from 512 to 4000, max_steps from 50 to 300, all produced identical results to cancellation alone.

This means for these puzzle depths, unguided beam search finds paths no shorter than the compressed inverse-walk from sample_submission. The search horizon is limited — beam search can't explore enough of the state space to find genuinely shorter paths.

## Implication

For gen 2, unguided beam search is a dead end. Any improvement beyond 46312 requires either:
1. A trained predictor to guide beam search
2. A fundamentally different algorithm (MITM with more depth, IDA* with pattern DB)
3. Valid Megaminx-specific algebraic identities

Pursuing "better unguided search tuning" (beam width, max_steps, restart strategies) is unlikely to help based on this evidence.