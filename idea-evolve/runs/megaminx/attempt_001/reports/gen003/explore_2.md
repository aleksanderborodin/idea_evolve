# Debrief Report — gen003 explore_2

## 1. Solutions and Scores

| Solution | Approach | Fitness | Valid | Time |
|----------|----------|---------|-------|------|
| sol01 | Compression (336 rules) + trained MLP predictor tail beam search | 44094 | Yes | ~437s |
| sol02 | Same approach via helper module | TIMEOUT | — | >900s |

**Best score: 44094** (vs gen002 best 44114, improvement of 20 moves / 0.05%)

## 2. What I Tried

- **sol01**: Two-phase compression + predictor-guided beam search. Phase 1 gets 44114 via empirical rules. Phase 2 trains MLP on random walks (50k, depth 20), then scans path tails with beam search (width 4096). Result: 20 moves saved across 10 puzzles.

- **sol02**: Refactored sol01 to use `helpers/trained_predictor_beam_search.py`. Timed out — the helper module's overhead (separate graph construction, less tight loop) made it too slow.

- **Informal experiments** (not submitted):
  - Deeper random walks (depth 50, 100k samples) — predictor still can't solve depth-20+
  - Training on actual path intermediate states — loss ~6000, useless
  - Greedy predictor search — fails even on depth-10
  - BFS tree from solved (depth 5, 1.37M states) — only 49 moves saved
  - Wider beams (8192, unguided) — max solvable depth ~15

## 3. What Information I Lacked

- **Architecture of Kaggle top-3 predictors.** I don't know what model architecture, training data depth, or training procedure they used. The flat MLP approach is clearly insufficient.
- **cayleypy internal APIs** for layer-by-layer BFS expansion. I couldn't find a way to enumerate states at specific depths efficiently.
- **Whether GNN predictors exist in cayleypy.** The library's `Predictor` accepts any `nn.Module`, but I don't know if GNN implementations are available or how to construct one for the Megaminx Cayley graph.

## 4. Facts That Might Be Wrong or Outdated

- **idea_008 claims "the pipeline is confirmed functional."** It is — but only for shallow puzzles (depth ≤12). The claim that this is "the only demonstrated path to the target" may be optimistic if the predictor can't generalize to actual puzzle depths.
- **The assertion that "beam_width must be 4x-32x larger" from idea_008.** In my testing, even beam_width=8192 couldn't solve depth-20. The required beam width grows exponentially, not linearly.

## 5. Was the State of Affairs Accurate?

Mostly yes. The SoA correctly identifies:
- Compression is exhausted at 44114
- Trained MLP predictor is the primary untested path
- Very_hard bucket dominates (74.8%)

**Missing/Understated**: The SoA doesn't emphasize that the predictor trained on depth-20 walks is fundamentally unable to guide beam search at the depths needed (100–1000). This isn't a beam-width problem — it's a predictor accuracy problem.

## 6. What I'd Do Differently

- Train the predictor on much deeper data (depth 100+ walks, even if fewer samples)
- Try a deeper MLP (4+ hidden layers) or a different architecture
- Use the compressed path's intermediate states as a training curriculum (start easy, increase depth)
- Explore whether cayleypy supports bidirectional search

## 7. What Surprised Me

- **How little the trained predictor helps.** I expected at least a few hundred moves of savings, not just 20.
- **Training on path intermediate states (depth 0–928) made the predictor WORSE.** The loss was ~6000 vs ~8 for random walks. The wide range of distances confused the model.
- **The BFS tree from solved has almost no overlap with compressed path intermediate states.** Only 21 hits out of ~80k intermediate states checked.

## 8. Helper Tools Feedback

- **`helpers/trained_predictor_beam_search.py`**: Works correctly. The `_PredictorMLP` handles dtype conversion properly. The `train_predictor()` and `guided_beam_search()` functions are well-designed. However, the module creates its own graph — when used inside a solution that also needs the graph for other purposes, this duplicates work and may cause GPU memory issues.
- **`helpers/core.py`**: All functions work as documented. `load_sample_submission_paths()` is not cached (correctly noted in docstring).

## 9. Time Budget

Not enough time. Training + evaluating takes ~7 minutes per solution. With the 15-minute timeout on sol02, I only got one scored solution. With more time I would have:
- Tried training on depth-100 random walks with a larger model
- Experimented with beam search at intermediate points along paths (not just the tail)
- Tested the BFS-tree approach at depth 7–8 (would need more RAM/time)

## 10. Specific Experiments to Run

1. **Train predictor on depth-100 walks, beam_width=65536**: See if deeper training data helps even with limited samples (10k walks at depth 100).
2. **Curriculum learning**: Train predictor incrementally — first on depth-10 data, then depth-20, then depth-50 — to see if progressive training improves generalization.
3. **Ensemble of depth-specific predictors**: Train separate predictors for each depth bucket (short, medium, hard, very_hard) and use the appropriate one for each puzzle.
4. **Graph neural network predictor**: Replace the flat MLP with a GNN that operates on the permutation structure directly. The cayleypy `Predictor` interface accepts any `nn.Module`.
