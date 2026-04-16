---
type: idea
id: idea_003
name: Predictor-guided beam search
lifecycle: active
confidence: 0.5
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: []
contradicted_by: []
related_ideas: [idea_004, idea_006, idea_007]
cluster: machine_learning
tags: [beam_search, predictor, ML, guided_search]
---

# Predictor-Guided Beam Search

## Summary

Train a model to predict distance-to-solved for any Megaminx state. Use this predictor as a heuristic in beam search to guide exploration toward promising states. This is the approach used by top Kaggle entrants (~8050 proxy).

## Evidence

**CONFIRMED WORKING (per research_1):**
- `Puzzles.megaminx()` returns CayleyGraphDef
- `graph.random_walks(width, length, mode='bfs')` produces training pairs
- `Predictor(graph, model)` wrapper exists
- Training loop: MSE 3.46 → 0.86 in 3 epochs on 1000 samples
- `beam_search(predictor=...)` accepts a predictor

**NEVER ACTUALLY TESTED:** No solution in gen_001 implemented a trained predictor. research_1 confirmed the pipeline works but ran out of time before running any experiment. Coverage matrix shows 0 central uses of idea_003.

**CONFLICT:** `cayleypy_beam_solver` helper does not expose `predictor` kwarg — agents must call cayleypy API directly.

## Status

ACTIVE but UNTESTED. Confidence 0.5 pending real evidence. The pipeline is confirmed functional but no agent has used it to beat compression.

## Why It Matters

If a predictor can guide beam search to find paths that compression misses (especially on very_hard bucket), the target of 15000 becomes realistic.

## What Must Happen in Gen 2

1. Run hamming predictor baseline FIRST (zero-cost, answers yes/no on whether guided search helps)
2. If hamming helps, train MLP predictor on random walks
3. Call `graph.beam_search(predictor=predictor)` directly (bypass helper)