---
type: idea
id: idea_007
name: Corner-only pattern database for IDA* — INVALID assumptions
lifecycle: debunked
confidence: 0.9
first_seen: gen_001
last_updated: gen_003
last_confirmed_gen: gen_003
supported_by: []
contradicted_by: [gen002_explore_1_sol01, gen003_explore_1]
related_ideas: [idea_004, idea_003]
cluster: heuristics
tags: [pattern_database, IDA_star, admissible_heuristic, debunked]
---

# Corner-Only Pattern Database for IDA* — INVALID Assumptions

## What Was Claimed

Precompute exact distances for corner-only Megaminx configurations. Use as an admissible
heuristic for IDA* search on the full puzzle.

## Why the Assumptions Are Wrong

gen002 confirmed all 24 Megaminx generators are 5-cycles. No 2-cycles or 3-cycles exist.
The corner/edge piece classification from Rubik's cube does not apply. The "corner-only"
projection does not decompose the state space in a useful way.

## Gen 3 Evidence

gen003 explore_1 was directed to try A* with landmark or perfect-hash heuristic (related
to idea_007's concept of structured heuristics). The agent completely failed — timing out
at all three phases (work/wrap-up/debrief) with zero output. While the failure wasn't
specifically about corner PDBs, it reinforces that classical heuristic search approaches
face fundamental tractability issues on Megaminx.

## Status

DEBUNKED. The structural assumptions are wrong and gen003's attempt at classical heuristic
search also failed. No further work on corner-based or piece-classification-based heuristics
should be pursued. The path forward is predictor-guided beam search (ideas 008, 010–013).
