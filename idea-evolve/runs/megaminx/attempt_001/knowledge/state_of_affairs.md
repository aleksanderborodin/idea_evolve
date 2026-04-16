---
generation: 1
best_score: 46312
trajectory: compression_baseline_established
last_updated_gen: 1
---

# State of Affairs — Gen 001

## Current Standing

Gen 1 established a compression baseline: **46312** (8.4% improvement over sample_submission's 50572) via X.-X cancellation. All 10 valid solutions converged to this same floor. The remaining gap to target (15000) is ~31k proxy moves — cannot be closed by cancellation or unguided search.

**Key fact:** The ML pipeline is confirmed functional (research_1) but **no solution actually ran predictor-guided beam search**. This is the primary path to the target and it has never been tested.

## What Works

- **X.-X cancellation (idea_001)**: ESTABLISHED. Used by all solutions. compression_ratio=0.9158.
- **Unguided beam search is dead**: Tested by 3+ solutions, widths 512-4000, steps 50-300 — all converged to exact same result as compression. State space (depth 8 = 3.5B states) makes coverage impossible.
- **cayleypy ML pipeline confirmed working**: graph.random_walks(), Predictor, beam_search(predictor=...) all verified by research_1.
- **Hamming predictor shortcut (idea_006)**: exists in cayleypy (`Predictor(graph, 'hamming')`), zero cost, completely untested.

## Current Frontier

The pipeline is stuck at the compression floor. No solution has beaten 46312. The next generation must test predictor-guided search — this is the only demonstrated path to the target.

Priority order:
1. idea_006: Hamming predictor baseline (zero-cost experiment, answers yes/no on guided search)
2. idea_003: Trained MLP predictor + beam_search(predictor=...)
3. idea_005: Systematic identity discovery (medium priority)
4. idea_007: Corner-only pattern database for IDA* (lower priority)

## Coverage Map

| Idea | Central Uses | Best Score | Status |
|------|-------------|------------|--------|
| idea_001 | 11 | 46312 | established |
| idea_002 | 1 | 50474 (invalid) | debunked |
| idea_003 | 0 | 46312 (unguided only) | active (NEVER predictor-tested) |
| idea_004 | 0 | 46312 | active (limited depth) |
| idea_005 | 0 | — | active (untested) |
| idea_006 | 0 | — | active (untested) |
| idea_007 | 0 | — | active (untested) |

**Unexplored**: idea_003 with trained predictor, idea_006 (hamming), idea_005, idea_007.

## Dead Ends

1. **Unguided beam search**: Confirmed ceiling = compression. All widths/steps tested.
2. **X.Y.-X commutator heuristic (idea_002)**: Debunked — Megaminx is non-commutative.
3. **Iterative cancellation**: No gains over greedy single-pass (pattern_002 confirmed).

## Open Questions

1. **Does any predictor beat compression?** CRITICAL — highest priority experiment. Hamming predictor is zero-cost; run it first.
2. **What beam params work with a trained predictor?** Unknown — never tested.
3. **Are there valid Megaminx-specific identities beyond X.-X?** idea_005 unexplored.
4. **What training data size is needed?** 1k? 10k? Unknown.
5. **Helper interface flaw**: `cayleypy_beam_solver` doesn't expose `predictor` — agents must call cayleypy API directly.

**very_hard bucket (ids 501-1000) = 74.8% of score.** Focus all effort there.