---
type: pattern
id: pattern_004
name: All 24 Megaminx generators are 5-cycles — corner/edge classification doesn't apply
lifecycle: active
confidence: 1.0
first_seen: gen_002
last_updated: gen_002
evidence: [gen002_explore_1_sol01, gen002_explore_1_sol03]
tags: [structure, generators, 5-cycles, piece_classification]
---

# All 24 Megaminx Generators Are 5-Cycles — Corner/Edge Classification Doesn't Apply

## Observation

**gen002_explore_1_sol01 discovered:** Every one of the 24 Megaminx generators has
5-cycle structure. There are no 2-cycles (edges in Rubik's cube sense) or 3-cycles
(corners in Rubik's cube sense). All 24 generators are 5-cycles.

**Implication:** Classic Rubik's cube piece classification (corner pieces with 3-cycles,
edge pieces with 2-cycles) does not apply to Megaminx. Any algorithm or heuristic
that relies on this distinction is INVALID for Megaminx.

**Specific impact on idea_007 (corner-only pattern database):** The idea_007 description
says "20 corners with orientations" and "corner-only state space (20 corners, orientations)
is small enough to enumerate exhaustively." This is based on wrong assumptions about
piece types. The "corner-only" heuristic does not have the same admissibility properties
as the Rubik's cube corner PDB because Megaminx's 5-cycles don't decompose into
corner-only and edge-only subspaces the same way.

## What This Means

- idea_007 (corner-only pattern database for IDA*) is based on incorrect structural assumptions
- Any heuristic that assumes a mix of 2-cycles and 3-cycles in the generator set is wrong
- The state space structure is fundamentally different from cube puzzles

## Confirmed By

gen002_explore_1_sol01's IDA* attempt confirmed that corner/edge classification fails:
the code's `get_corner_positions()` found no 2-cycles or 3-cycles in the generator set,
only 5-cycles.
