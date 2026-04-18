# State of Affairs — Gen 002

## Current Standing

Gen 2 achieved **44114** — a 4.7% improvement over gen 1's 46312 baseline via empirical algebraic identity compression (idea_009). Six explore_2 solutions independently confirmed this floor. The gap to target (15000) is ~29k proxy moves. Compression alone is exhausted; the next breakthrough requires trained-predictor-guided beam search.

**Generations run:** 2. **Trajectory:** compression floor broken, primary path untested.

## What Works

- **X.-X + commutator/conjugation compression (idea_001 + idea_009)**: Established. 6 solutions → 44114 (compression_ratio=0.8723). Empirical discovery outperforms systematic enumeration (336 rules > 432 rules).
- **Hamming predictor is useless (idea_006)**: Debunked. Zero advantage over unguided at every beam width tested.
- **All 24 Megaminx generators are 5-cycles**: Confirmed. Corner/edge classification from cube puzzles does not apply.

## Current Frontier

**idea_008 (trained MLP predictor) — NEVER TESTED end-to-end.** research_1 confirmed the pipeline is functional (`random_walks` → train MLP → `beam_search(predictor=...)`), but no agent executed it. exploit_1 hit a state-encoding error and fell back. This is the only demonstrated path to the target.

Priority for gen 3:
1. Run `graph.random_walks(50000, 20)` → train MLP → `beam_search(predictor=...)` on hard/very_hard buckets
2. Combine compression (44114 floor) + trained-predictor beam search (从未 tested)
3. Test beam_width=[1024, 2048, 4096, 8192] with trained predictor

## Coverage Map

| Idea | Central Uses | Best Score | Status |
|------|-------------|------------|--------|
| idea_001 (cancellation) | 16 | 46312 | established (STALE) |
| idea_005 (identity discovery) | 6 | 44114 | established |
| idea_008 (trained MLP) | 0 | — | active (NEVER TESTED) |
| idea_003 (predictor beam) | 0 | 46312 | active (pipeline confirmed, untrained) |
| idea_006 (hamming) | 0 | 46312 | DEBUNKED |
| idea_009 (empirical algebraic) | 6 | 44114 | active |

**Unexplored**: idea_008 (trained MLP) — 0 trials. compression + beam search combination — 0 trials.

## Dead Ends

1. **Unguided beam search**: Adds nothing over compression at any beam width. Confirmed by 10+ solutions.
2. **Hamming predictor**: Zero advantage. Debunked.
3. **X.Y.-X heuristic (idea_002)**: Invalid for non-commutative Megaminx. Debunked.
4. **idea_007 corner-only PDB**: All generators are 5-cycles — the corner/edge classification assumptions are wrong. Invalidated.

## Open Questions

1. **Does trained MLP predictor beat 44114 compression?** CRITICAL — never run. The central unknown.
2. **Does compression + beam search combined outperform either alone?** Never tested. Low-hanging fruit.
3. **What training depth generalizes to depth-500+ puzzles?** Trained on depth-20; unknown if it generalizes.
4. **Why did systematic enumeration (432 rules) underperform empirical (336 rules)?** Test-set specificity matters more than mathematical completeness.
5. **Beam_mode='advanced' bug**: Returns path=None despite path_found=True. Must use 'simple' mode.

**very_hard bucket (ids 501-1000) = 74.8% of score.** All predictor experiments must focus there.