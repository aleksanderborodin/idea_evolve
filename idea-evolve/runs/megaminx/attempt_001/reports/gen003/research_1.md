# Debrief Report — research_1, Gen 003

## 1. What I Tried

1. **Deep source code analysis of cayleypy library.** Read all key files: `predictor.py`, `beam_search.py` (both modes), `random_walks.py`, `models/models.py`, `models/models_lib.py`, `cayley_graph.py`, `cayley_graph_def.py`, `algo/bfs_mitm.py`, `algo/interactive_bfs.py`, `algo/beam_search_result.py`. This gave a complete understanding of every API, parameter, and internal mechanism.

2. **BFS growth rate measurement.** Ran BFS to depth 6 on GPU (19.4M states, ~1s) and confirmed depth 7 OOMs. Growth rate is ~14× per level (not 24× due to state deduplication).

3. **Model architecture comparison.** Trained two models side by side on the same data:
   - Raw integer MLP (like existing helper): final loss 4.57
   - Embedding-based MLP: final loss 0.86 (5.3× better)

4. **MITM + beam search experiment.** Tested `bfs_result_for_mitm` parameter with hamming predictor. Confirmed MITM finds optimal path (len=10) for sid=10 where unguided finds len=12. Also discovered hasher compatibility requirement (CPU BFS + GPU beam = silent failure).

5. **One-hot encoding OOM investigation.** Confirmed that one-hot encoding (120×120=14,400 features) causes OOM during beam search inference at beam_width ≥ 4096. The Predictor's batching (via `graph.batch_size`) can mitigate this, but embedding-based models are more memory-efficient.

6. **Attempted full end-to-end pipeline.** Tried to run the complete recipe (BFS + train embedding MLP + MITM beam search on multiple puzzles) but ran into GPU memory issues and timeouts. The experiments were partially successful (individual components verified) but the full benchmark didn't complete within the session.

## 2. What Information I Lacked

1. **Kaggle top solution details.** Couldn't access the actual code of top-scoring notebooks. The competition page returned minimal content via web fetch. This is the biggest gap — we're guessing at what works while the competition leaders have already demonstrated approaches scoring ~8k proxy.

2. **GPU memory availability during the session.** Other processes (PID 59138, 60215, etc.) were consuming GPU memory throughout my experiments, leaving only 8-10GB free on the 16GB GPU. This limited my ability to run larger experiments.

3. **The `_to_kaggle_name` mapping from generator indices to Kaggle move names.** I discovered it exists in the helper (`cayleypy_beam_solver` uses it), but the exact mapping from generator index → Kaggle name wasn't immediately obvious. The helper already has this.

## 3. What Given Facts Might Be Wrong or Outdated

1. **State of Affairs says "trained MLP predictor NEVER TESTED end-to-end"** — this is accurate. No agent has successfully run the full pipeline. The helper exists but has the wrong model architecture.

2. **Idea_008 pipeline code uses raw integer MLP** — this is suboptimal but not "wrong" per se. The pipeline will work, just with much worse predictor quality.

3. **Description.md says "CPU-only" for beam search** — incorrect. CayleyPy automatically uses GPU when available. The GPU is the reason beam_width=4096 is tractable at all.

## 4. Was the State of Affairs Accurate?

Mostly accurate. The strategic assessment (compression is exhausted, trained predictor is the only path) is correct. The dead ends list is accurate. The coverage matrix correctly reflects what has been tried.

**Missing from State of Affairs:**
- The `bfs_result_for_mitm` parameter in beam search (cayleypy built-in MITM)
- The model architecture issue (raw integers vs one-hot/embedding)
- BFS depth 6 as a source of exact-distance training data
- The embedding-based model approach for memory efficiency

## 5. What Would I Do Differently With More Context

1. **Read the cayleypy source code in gen001, not gen003.** Two generations were spent guessing at the API. The source code is clean, well-documented, and reveals capabilities (MITM, interactive BFS, nbt random walks) that no one discovered.

2. **Test the helper before the competition.** The existing `trained_predictor_beam_search.py` helper has the wrong model architecture. If it had been tested even once in gen001, this would have been caught immediately.

## 6. Specific Experiments to Run

1. **The full recipe from Finding 5.** BFS depth 6 → train embedding MLP → MITM beam search on all 101 proxy puzzles. This is the #1 priority.

2. **Beam width sweep with MITM.** Test beam_width=[1024, 2048, 4096, 8192, 16384] with MITM depth 6 on a fixed set of puzzles (sids 10, 50, 100, 200, 500). This determines the optimal beam width per bucket.

3. **BFS data vs random walk data training comparison.** Train the same model architecture on (a) BFS depth 6 exact data (19.4M samples), (b) random walks BFS mode (800k samples, length 20), (c) combined. Measure predictor MSE and beam search success rate.

4. **Embedding dimension sweep.** Test embed_dim=[8, 16, 32, 64] with fixed hidden layers. Measure training loss, inference memory, and beam search success rate.

## 7. What Surprised Me

1. **The existing helper's model architecture is fundamentally wrong.** I expected implementation bugs or parameter tuning issues, not a categorical-vs-ordinal representation error. This single finding explains why the trained predictor approach has been stalled for 2 generations.

2. **BFS depth 6 produces 19.4M states in 1 second.** I expected BFS to be much slower. The GPU-accelerated BFS with bit encoding (14 ints per state instead of 120) is extremely fast.

3. **MITM + beam search is built into cayleypy but no one knew.** The `bfs_result_for_mitm` parameter is documented in the beam_search docstring but wasn't mentioned in any Kaggle notebook, the helper README, or any agent prompt.

4. **The hasher compatibility issue.** Computing BFS on a different graph instance silently breaks MITM. This is a footgun that would be very hard to debug without reading the source code.

## 8. Helper Tools Feedback

- **`trained_predictor_beam_search.py`**: The pipeline structure is good (generate walks → train → beam search), but the model architecture is wrong (Finding 1). The `_PredictorMLP` should be replaced with an embedding-based model. The `build_graph()` and `train_predictor()` helper functions are well-designed but need the architecture fix.

- **`helpers.core.cayleypy_beam_solver`**: This function doesn't expose the `predictor` or `bfs_result_for_mitm` parameters. Agents that want MITM+beam must call `graph.beam_search()` directly instead of using this helper. Consider adding a new helper that exposes these parameters.

- **Missing helper**: A `bfs_training_data()` function that computes BFS to depth 6 and returns (X, y) training data + bfs_result for MITM would be extremely useful. Currently every agent has to figure this out independently.

## 9. Time Budget

I had enough time for the source code analysis and targeted experiments, but not enough to run the full end-to-end benchmark. The critical missing experiment is: train the embedding MLP on BFS data, then run predictor+MITM beam search on all 101 proxy puzzles and measure the actual fitness.

With more time, I would have:
1. Completed the full benchmark (likely needs 15-20 minutes of GPU time)
2. Tested the approach on the very_hard bucket (sids 500-1000) to see if any of them can be solved
3. Optimized the training hyperparameters (learning rate schedule, epochs, embedding dim)
4. Tried the combined approach: compression (44114 baseline) for fallback + predictor+MITM for search
