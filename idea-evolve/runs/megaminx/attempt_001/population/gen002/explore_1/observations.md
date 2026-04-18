# Observations — gen002_explore_1

## What I tried

1. **IDA* with corner PDB** — Depth-first admissible search. Idea was to find truly optimal paths for shallow puzzles while falling back to sample_submission for deep ones. **Failed:** Timed out on evaluation. The BFS depth 5 PDB was too shallow to be useful as a heuristic, and the search still explored massive state spaces.

2. **Hamming-predictor beam search** — Zero-cost guided search experiment (EXP-1 from gen001 suggestions). **Failed:** UTF-8 file corruption during write caused invalid syntax. Score = sentinel 1e9.

3. **Enhanced compression + beam fallback** — Multi-pass X.-X cancellation for all puzzles, then hamming-guided beam for hard/very_hard. **Score: 46,312** — identical to gen001 baseline. Compression ceiling confirmed.

4. **Timing-budget-aware hybrid** — Enhanced compression + timed beam on deepest very_hard puzzles. **Score: 46,312** — no improvement.

## Key discovery

**Megaminx has NO 3-cycles or 2-cycles.** All 24 generators use 5-cycles only. This means:
- Classic Rubik's cube corner/edge piece classification doesn't apply
- A "corner-only" pattern database was based on wrong assumptions about piece types
- The state space structure is fundamentally different from cube puzzles

## What the compression floor means

All 4 solutions that produced scores converged to 46,312 with compression_ratio=0.9158. This means:
- ~8.4% compression of sample_submission paths via X.-X cancellation
- The remaining 91.6% of path length is NOT cancellable via adjacent-pair patterns
- The theoretical ceiling for compression-only approaches is likely ~0.85-0.90

## Where the score is

very_hard bucket = 34,634 / 46,312 = **74.8% of total score**. Any meaningful improvement must come from solving deeper puzzles better.

## What didn't work

- IDA* depth-first search (too slow, wrong heuristic assumptions)
- Enhanced multi-pass compression (no improvement over single-pass)
- Beam search without trained predictor (converges to compression ceiling)

## What would work

- **Trained MLP predictor + guided beam search** (EXP-2 from gen001 suggestions)
- Higher beam widths + more steps on GPU-accelerated hardware
- The gen001 state_of_affairs correctly identified predictor-guided beam as "highest-leverage direction" — confirmed by this generation's failure to beat compression with anything else.