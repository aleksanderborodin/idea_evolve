# Research Debrief — gen001_research_1

## What did you try?

1. **Read all available documentation and problem files** — description.md, initial_ideas.md, initial_facts.md, helpers/core.py, baseline solutions. Established baseline: sample_submission = 50,572 (zero-search floor), random baseline = 101,000,000.

2. **Fetched Kaggle notebooks via kaggle CLI**:
   - `mitchell11/cayleypy-megaminx-base-litvinov-michael` (20 votes) — graph structure analysis, growth function, spectrum. NOT a solver.
   - `alexandervc/cayleypy-megaminx-meetinthemiddle-bfs-solver` (4 votes) — MITM implementation with BFS depth 5-6. CONFIRMED working pattern.
   - `mitchell11/cayleypy-megaminx-ml-base-litvinov-michael` (5 votes) — ML-based predictor training pipeline. CONFIRMED working API.

3. **Verified cayleypy API in this environment**:
   - `Puzzles.megaminx()` → CayleyGraphDef ✓
   - `graph.random_walks(width, length, mode='bfs')` → (X, y) training pairs ✓
   - `Predictor(graph, model)` → predictor wrapper ✓
   - Training loop works (MSE drops from 3.46 → 0.86 in 3 epochs on 1000 samples) ✓
   - **Did not fully time** `graph.beam_search` with predictor on CPU — timed out at 60s on one test.

4. **Attempted to fetch 3 more notebooks** (`lilypilly/cayleypy-cube-train-and-solve-smallmodel`, `fedimser/beam-search-with-cayleypy`) — kaggle CLI hung repeatedly. These are not available locally.

## What information did you lack?

1. **No generation-1 agent outputs** — no cluster summaries, no active ideas, no group notes. The State of Affairs was empty. Could not build on previous agent discoveries.

2. **No paper summaries** in `papers/summaries/`. No academic literature was downloaded or reviewed. The search space for algorithmic improvements may have blind spots.

3. **No timing data for beam_search + predictor on GPU** — the RTX 5060 Ti should be significantly faster than CPU for the model forward pass. I could not measure whether GPU makes guided beam search fast enough to be practical for 101 puzzles.

4. **The growth function upper bound**: BFS to depth 9 reaches 48B states — obviously infeasible. But the exact state count at depth 8 (3.5B) is also infeasible. The tractable BFS depth is likely 5-7. The MITM approach would only help for depths ≤ 2× the BFS depth.

5. **No information about the actual top Kaggle solution architectures** — only notebook titles and vote counts. The actual model architectures, training data sizes, beam widths, and ensembling strategies of the 80k-scoring solutions are not documented in any notebook I could access.

## What given facts might be wrong or outdated?

1. **`PROXY_SIZE` in helpers/README.md says `100`** but the code in `helpers/core.py` and `description.md` both say `101` (ids 0,10,20,...,1000). The README is misleading but the actual code is correct.

2. **The claim "cayleypy requires torch; CPU torch is fine"** in `description.md` — verified correct for graph construction and BFS. Unclear if the predictor + beam_search pipeline is fast enough on CPU for the eval budget (~7 min for 101 puzzles). This needs GPU to be practical.

## Was the State of Affairs accurate?

Yes — it correctly stated that nothing had been explored yet. The initial ideas and facts were comprehensive and well-structured. The brief's directive to "focus on patterns from Kaggle notebooks" was appropriate and actionable.

## What would you do differently with more or different context?

1. **Access to the fedimser/beam-search-with-cayleypy notebook** (51 votes, best beam search tuning reference). I couldn't fetch it after multiple attempts. The beam search parameter tuning (beam_width vs max_steps vs predictor quality tradeoffs) would be the most actionable content for implementation.

2. **GPU timing data** — running a timed test of predictor-guided beam search on a few dozen puzzles would constrain whether the current approach is even feasible in the eval budget.

3. **Pre-existing paper summaries** — no academic papers on Megaminx solvers or related permutation puzzle AI were in the papers/summaries/ directory. A literature search would have provided theoretical grounding.

4. **The `cayleypy_beam_solver` wrapper in helpers/core.py** doesn't support the `predictor` kwarg — it only passes `beam_width` and `max_steps`. Agents using the helper can't access the predictor. They need to call the cayleypy API directly.

## Specific experiments to run?

1. **Quick ML baseline** (highest priority): Train the simplest predictor (single hidden layer, 50k random walks length 20), use it in beam_search for all 101 proxy puzzles. Measure time and score. Compare against sample_submission (50,572) and target (15,000).

2. **MITM coverage test**: Precompute BFS to depth 5, 6, 7. For each, measure what fraction of proxy puzzles have optimal distance ≤ 2×depth. This quantifies MITM's ceiling.

3. **Move cancellation measurement**: Apply move cancellation to sample_submission paths. Measure the actual compression ratio achieved. Expected 5-15%.

4. **Predictor generalization test**: Train predictor on length-20 walks only. Evaluate on puzzles with depth 50, 100, 200. Measure whether the predictor's estimates are well-calibrated for depths outside the training distribution.

## What surprised you?

1. **How readily the full ML pipeline works in this environment** — `Puzzles.megaminx()`, `random_walks`, `Predictor`, `beam_search(predictor=...)` all work out of the box. No API surprises.

2. **The base notebook was mostly graph theory analysis** — growth function, eigenvalues, spectrum. Not a solver. The actual solver patterns were in the ML and MITM notebooks, which were harder to fetch.

3. **The growth function numbers** are staggering: depth 8 = 3.5 billion states, depth 9 = 48 billion. This makes it crystal clear why single-pass BFS/beam cannot work for hard/very_hard buckets, and why a learned predictor is essential for directing the search.

4. **The `Predictor(graph, 'hamming')` shortcut exists** — a built-in Hamming-distance predictor without training. This is a zero-cost baseline to compare against a trained model.

## Helper tools feedback

**helpers/core.py** — Well-designed. The lazy import of cayleypy is correct (heavy). `cayleypy_beam_solver` is a useful convenience wrapper but **does not expose the `predictor` kwarg** that `graph.beam_search` supports. For the ML approach, agents must call the cayleypy API directly rather than through the helper.

**helpers/README.md** — Wrong `PROXY_SIZE` (says 100, should be 101). Otherwise accurate.

**What helper do I wish existed**: A `guided_beam_solver(state, model, beam_width, max_steps)` function that wraps the full predictor + beam_search pipeline. This would let agents call one function with a trained PyTorch model instead of having to import cayleypy directly and manage the API themselves.

## Time budget

**Not enough time to finish**: I needed at least one more hour to:
1. Successfully fetch the `fedimser/beam-search-with-cayleypy` notebook (the best beam search tuning reference)
2. Run the actual ML pipeline on a few proxy puzzles to get a real timing + score estimate
3. Verify the MITM approach timing on 101 puzzles
4. Test the move-cancellation compression ratio on sample_submission

**What I would do next with more time**:
- Run the ML pipeline end-to-end: train on 50k random walks (length 25), evaluate on all 101 proxy puzzles with beam_width=2000, record real fitness, timing, and per-bucket breakdown.
- This single experiment would answer whether the target (15k) is achievable in gen 2 and where the bottlenecks are.
