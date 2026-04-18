---
type: idea
id: idea_007
name: Corner-only pattern database for IDA* — INVALID assumptions
lifecycle: active
confidence: 0.2
first_seen: gen_001
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: []
contradicted_by: [gen002_explore_1_sol01]
related_ideas: [idea_004, idea_003]
cluster: heuristics
tags: [pattern_database, IDA_star, admissible_heuristic, invalidated]
---

# Corner-Only Pattern Database for IDA* — INVALID Assumptions

## What Was Claimed

Precompute exact distances for corner-only Megaminx configurations. The "corner-only"
state space was assumed to be small enough to enumerate exhaustively. Use the
precomputed distance as an admissible heuristic for IDA* search on the full puzzle.

## Why the Assumptions Are Wrong

**gen002_explore_1_sol01 confirmed:** All 24 Megaminx generators have 5-cycle structure.
There are NO 2-cycles or 3-cycles in the generator set. The idea's description assumed
a mix of 2-cycles and 3-cycles (like Rubik's cube corners/edges) that doesn't exist
in Megaminx.

The "corner-only" projection does not decompose the state space the same way.
The heuristic's admissibility depends on corner/edge piece classification that is
INVALID for Megaminx.

## Evidence

gen002_explore_1_sol01's IDA* attempt:
- Built a BFS corner PDB up to depth 5
- The corner configuration space did NOT provide useful guidance because
  all generators are 5-cycles, not a mix of 2-cycles and 3-cycles
- The search still explored massive state spaces and timed out

## Status

ACTIVE but DESPERATELY NEEDS REVISION. The structural assumptions are wrong.
The idea needs either:
1. A reformulation based on correct Megaminx state space structure, OR
2. Reclassification as debunked if no valid reformulation exists

The pattern database approach is theoretically sound for IDA* — but the specific
"corner-only" decomposition is invalid for Megaminx's generator structure.
