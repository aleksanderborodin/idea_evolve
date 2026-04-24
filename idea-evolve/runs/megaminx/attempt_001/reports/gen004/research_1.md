# Debrief Report — research_1, Gen 004

## 1. What I Tried

1. **Searched for Kaggle cayley-py-megaminx competition write-ups.** Kaggle pages are JS-rendered (no server-side HTML), so WebFetch returned empty page shells. Google search for "cayley-py-megaminx solution" and "megaminx kaggle writeup" returned no public write-ups from top solvers. The competition is relatively new (2025) and appears to have no third-party analysis.

2. **Downloaded and read the full CayleyPy RL paper (arXiv:2502.18663).** 32-page paper by Chervov et al. with 33 co-authors. Read the complete text (~2200 lines). This is the paper by the team that created both the CayleyPy library AND the Megaminx Kaggle competition. It describes their complete pipeline: diffusion distance training → DQN refinement → beam search.

3. **Downloaded and read the abstract of the CayleyPy-1 paper (arXiv:2502.13266).** "A Machine Learning Approach That Beats Large Rubik's Cubes" — achieves 98% optimality on 3×3×3, beats all Santa 2023 competitors on 4×4×4/5×5×5. Uses the same diffusion distance + beam search pipeline.

4. **Analyzed CayleyPy source code.** Read `models/models.py` (MlpModel architecture), `predictor.py` (Predictor class with batching), `cayley_graph.py` (BFS, beam_search, find_path_to), `algo/beam_search.py` (simple and advanced modes with MITM). This was the most valuable research — it revealed that the official model uses one-hot encoding (NOT raw integers as we assumed), and the advanced beam mode implements non-backtracking.

5. **Read DeepCubeA Nature paper abstract.** Agostinelli et al. 2019, Nature MI. 60.3% optimal on 3×3×3. Uses Weighted A* with learned heuristic. Significantly outperformed by CayleyPy's beam search approach (98% optimal). Confirms beam search is the winning paradigm, not A*.

6. **Read the CayleyPy GitHub README.** Found the list of Kaggle competitions, the model training/upload process, and the library overview. Confirmed no pretrained model exists for Megaminx (only LRX-16 and LRX-32).

## 2. What Information I Lacked

1. **The actual code/notebooks of Kaggle top-3 solvers.** These are private — no write-ups exist. We're inferring their approach from the CayleyPy team's published papers and library, which is a reasonable inference since the competition was created by the same team to benchmark their approach.

2. **Detailed comparison between "simple" beam + MITM vs "advanced" beam + non-backtracking.** The CayleyPy paper benchmarks non-backtracking for LRX graphs but doesn't directly compare it against MITM for Megaminx. These are mutually exclusive in the current implementation.

3. **GPU memory profiling for MlpModel at various beam widths on our specific hardware.** My calculations suggest beam_width=65536 is feasible with batch_size=2048, but this needs empirical verification.

## 3. What Given Facts Might Be Wrong or Outdated

1. **Idea_011 claims "the CayleyPy model uses raw integers" — WRONG.** CaylePy's `MlpModel` uses one-hot encoding via `nn.functional.one_hot()`. Our custom `_PredictorMLP` in best.py used raw integers (just casting to float), which is indeed wrong. But the fix is not to build a custom embedding model — it's to use CayleyPy's built-in `MlpModel`.

2. **The SoA says "trained MLP predictor NEVER TESTED end-to-end"** — still true. But the finding is that the architecture we should be testing is CayleyPy's `MlpModel` with one-hot, not our custom embedding model from idea_011.

3. **The SoA lists idea_013 (combined recipe) with "Conservative: ~43000-44000, Optimistic: ~35000-40000"** — these estimates are likely too pessimistic if we use the correct architecture (one-hot MlpModel) at adequate beam width (65536). The CayleyPy team achieves 98% optimality on Rubik's with this approach. Megaminx is harder but not fundamentally different.

## 4. Was the State of Affairs Accurate?

Mostly accurate for what it describes. However:

**Missing critical insight:** The SoA focuses on "embedding MLP vs raw integer MLP" (idea_011) as the architecture fix. This misses that CayleyPy's official model already uses one-hot encoding (which is more memory-expensive but proven to work). The real fix is to USE the library's built-in model, not to build a custom one.

**Missing: beam width as the dominant parameter.** The SoA mentions beam_width=4096 but doesn't highlight that competitive solutions use 16-256× wider beams. The CayleyPy paper is explicit: "beam size is one of the most important parameters" and "solution length is almost linearly improving on logarithm of beam size."

**Missing: random walks vs BFS for training data.** The SoA presents BFS depth-6 data (idea_010) as "strictly superior to random walks" — but this is wrong for the use case. BFS gives exact labels for distances 0-6 only, while the CayleyPy team deliberately uses random-walk-based diffusion distance as their primary training signal because it covers a much wider range of distances.

## 5. What Would I Do Differently With More Context

1. **Read the CayleyPy papers and source code in gen 001.** The entire architecture question (raw integer vs embedding vs one-hot) was answered in the published code. Three generations of confusion could have been avoided.

2. **Focus on beam_width scaling earlier.** The single biggest lever is beam width, not model architecture. Even a mediocre predictor at beam_width=65536 likely beats a great predictor at beam_width=4096.

## 6. Specific Experiments to Run

1. **MlpModel + random walks + beam_width=65536 + MITM.** The full pipeline, end-to-end, on all 101 proxy puzzles. This is THE experiment.

2. **Beam width sweep: 4096, 8192, 16384, 32768, 65536.** On a fixed set of 10 puzzles (2 per bucket). Plot path length vs log(beam_width). This tells us where the performance curve flattens.

3. **Simple mode + MITM vs Advanced mode + non-backtracking.** On the same 10 puzzles, compare both modes at the same beam_width. This determines which mode to use in production.

4. **Random walks training vs BFS training.** Train the same MlpModel on (a) random walks data and (b) BFS depth-6 data. Compare predictor MSE and beam search success rate.

## 7. What Surprised Me

1. **CayleyPy's official model uses one-hot encoding, NOT raw integers.** We spent 2 generations thinking the CayleyPy approach was "raw integer MLP." It was actually one-hot all along — our custom implementation was the broken one.

2. **The CayleyPy team's approach is exactly what we should be doing.** There's no secret sauce — diffusion distance + beam search + large beam_width IS the winning approach. Our gap is execution quality, not paradigm choice.

3. **DeepCubeA's 60.3% optimality is easily beaten by beam search (98%).** The A*/BWAS approach from DeepCubeA is not state-of-the-art. The simpler beam search approach is both faster and more accurate.

4. **Non-backtracking in beam search is extremely effective.** The CayleyPy-2 paper shows it quadruples success rate (17.6% → 69.7%) for the same beam width. This is a free performance boost we haven't tried.

## 8. Helper Tools Feedback

- **`helpers.core.cayleypy_beam_solver`**: Still doesn't expose predictor, MITM, beam_mode, or history_depth parameters. Agents that need the full pipeline must call `graph.beam_search()` directly, which means re-implementing the Kaggle name translation. This helper is only useful for unguided beam search (which is a dead end per our findings).

- **Missing helper**: A `full_pipeline_solver()` function that encapsulates: (1) create graph with proper batch_size, (2) train MlpModel on random walks, (3) run BFS for MITM, (4) run beam search with predictor + MITM + configurable beam_width, (5) translate results to Kaggle move names. Every agent currently has to re-implement this from scratch.

## 9. Time Budget

I had sufficient time for the literature review and source code analysis. The CayleyPy RL paper was the most valuable source — reading it completely took about 30 minutes but saved potentially 3+ generations of misguided effort.

With more time, I would have:
1. Downloaded and read the CaylePy-1 paper (arXiv:2502.13266) fully, not just the abstract
2. Searched for the Douglas et al. 2025 "Diffusion Models for Cayley Graphs" paper (arXiv:2503.05558) which is a newer approach
3. Looked at the CayleyGraphProp GNN paper (arXiv:2410.03424) in more detail
4. Profiled GPU memory requirements for the proposed beam_width=65536 pipeline empirically
