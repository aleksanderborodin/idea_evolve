# Observations — gen003 explore_2

## Approaches Tried

### sol01: Compression + trained-predictor tail beam search — **fitness 44094**
Two-phase approach combining empirical identity compression (336 rules) with a trained MLP predictor for beam search optimization of path suffixes.

**Phase 1** (Compression): Re-implemented the 336-rule empirical compression from gen002. Achieved 44114, matching the established baseline.

**Phase 2** (Trained predictor beam search): Generated 50k random walks (depth 20) from solved state, trained MLP (120→256→128→1, MSE, 10 epochs), then for each compressed path, iteratively tried beam search (width=4096) on suffixes of length 2–15 from the tail. Multiple passes until no more improvements.

**Result**: 44114 → 44094. Only 20 moves saved across 10 puzzles. Beam search with the trained predictor can only solve suffixes ≤12 moves from solved. The depth-20 training data does NOT generalize to deeper distances.

### sol02: Same approach using helper module — **TIMED OUT (>15 min)**
Identical strategy to sol01 but using the `helpers.trained_predictor_beam_search` module. The evaluation timed out — likely the beam search loop was slower due to the helper's overhead or the graph construction being duplicated.

### Approaches explored but not submitted (informal testing)

1. **Trained predictor with deeper walks (depth 50, 100k walks)**: Still couldn't solve depth-20+ puzzles. Loss remained high (44+). The predictor fundamentally can't generalize to the actual puzzle depths (100–1000).

2. **Predictor trained on path intermediate states**: Trained on actual compressed-path intermediate states (known distances 0–928). Loss was ~6000 — far too high for useful guidance.

3. **Greedy predictor search**: At each step, try all 24 moves, pick the one with lowest predicted distance. Failed even on depth-10 puzzles — the predictor isn't accurate enough for greedy decisions.

4. **BFS from solved state (depth 5)**: Built a 1.37M-state BFS tree. Only 49 moves saved across 21 puzzles — the compressed paths go through states that rarely intersect the BFS tree.

5. **Wider beam widths (8192, unguided)**: Could solve depth-10 reliably, depth-15 sometimes, depth-20 almost never.

## Key Findings

1. **The trained MLP predictor is the bottleneck.** Trained on depth-20 random walks, it cannot guide beam search beyond ~12 moves from solved. This means the "Phase 2" approach can only shorten the very tail of long paths.

2. **Compression ceiling is real.** Even with longer patterns (up to length 6), no new savings were found. The 336-rule empirical compression at 44114 is the true compression-only floor.

3. **The gap to target (15000) requires a fundamentally different predictor.** The Kaggle top-3 solutions (8050 proxy equivalent) almost certainly use predictors trained on much deeper data, possibly with different architectures (GNNs, not just MLPs).

4. **The helper module `trained_predictor_beam_search.py` works correctly** — it handles the int64→float32 dtype conversion that blocked gen002 agents. The `_PredictorMLP` class's `forward()` method converts input dtype automatically.

5. **Segment-by-segment beam search is impractical** — with beam_width=4096, each beam call takes ~1s. For a 500-move path with 50 checkpoints, that's 50s per puzzle, ~5000s for 101 puzzles. Only tail optimization is fast enough.

## What Would Help

1. **A GNN-based predictor** that understands the permutation structure, not just treats states as flat vectors.
2. **Training data at matching depths** — the random walks generate states at depth 0–20, but puzzles need guidance at depth 100–1000.
3. **Iterative deepening search** with the predictor as heuristic (like IDA*) — but this requires a predictor accurate enough for pruning.
4. **Multi-source BFS** from solved state to depth 8–10 stored in a hash table — would help find short paths from any state within 10 moves of solved, but this is a minor improvement.
