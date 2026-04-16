# Research Debrief — gen002_research_1

## 1. What did you try?

### Kaggle Notebook Fetching (SUCCESS)
Fetched 3 notebooks from Kaggle:
- `alexandervc/cayleypy-megaminx-beamsearch-hamming` (2 votes) — uses beam_width=65536 + hamming predictor
- `alexandervc/cayleypy-megaminx-meetinthemiddle-bfs-solver` (4 votes) — MITM with BFS diameter 5-6
- `mitchell11/cayleypy-megaminx-first-steps` (13 votes) — MLP predictor training recipe

### Controlled Beam Search Experiments (SUCCESS)
Ran controlled experiments comparing hamming vs unguided at identical beam widths. Key finding: **zero difference** at any beam width. Both find identical path lengths.

Tested beam_width scaling: 2048 → 32768 → 65536. Found that depth-10 puzzles need beam_width~32768 to solve optimally, but this becomes intractable for deeper puzzles.

### MITM Experiments (SUCCESS)
Ran MITM with BFS diameter 5 and 6. Found that diameter=5 covers 1.4M states; diameter=6 covers 19.4M states. Growth is exponential. MITM can only solve depth ≤ 12 puzzles, which is useless for this competition where the shallowest test puzzle is depth 10.

### beam_mode Experiments (SUCCESS)
Discovered that `beam_mode='advanced'` is ~2x faster but has a bug where `return_path=True` still returns `path=None`. Must use `beam_mode='simple'` to get actual paths.

### Graph Device Check (SUCCESS)
Confirmed that `CayleyGraph(gdef)` uses CUDA/GPU automatically when torch.cuda is available. description.md "CPU-only" claim is wrong.

## 2. What information did you lack?

- **No information about what beam_width actually works for depth 20-100 puzzles.** My experiments timed out at beam_width=32768 for depth 20+. I don't know the crossover point where beam search becomes useless for medium/hard buckets.
- **No trained MLP predictor baseline.** I confirmed hamming is useless but couldn't train and test an MLP in the time budget. This is the most critical missing experiment.
- **No clarity on how beam_width affects wall-clock time at depth 100+.**
- **The actual top-solver architectures from Kaggle** — only notebook titles were accessible. The actual model architectures, training data sizes, beam parameters of the 80k-scoring solutions are not documented in any accessible notebook.

## 3. What given facts might be wrong or outdated?

- **description.md "CPU-only" claim**: Confirmed wrong — CayleyGraph uses CUDA automatically.
- **helpers/README.md PROXY_SIZE=100 typo**: Still present (should be 101).
- **The claim that hamming predictor is untested**: It IS tested in the beamsearch-hamming Kaggle notebook (which I fetched). The notebook confirms it works but the author still only achieves modest improvements.
- **The idea that beam_width=65536 is tractable**: It IS tractable for depth~10 puzzles (5-6s each). For depth 20+, it times out.

## 4. Was the State of Affairs accurate?

Yes, with one important correction: The State of Affairs says idea_006 (hamming predictor) has never been tested. I have now tested it, and the answer is: **hamming provides zero advantage over unguided search**. This should update idea_006's confidence from 0.8 to a debunked/low status.

The State of Affairs correctly identifies predictor-guided search as the primary path. It just didn't know that hamming doesn't work.

## 5. What would you do differently with more or different context?

1. **Train an MLP predictor immediately** instead of spending 20 minutes on hamming experiments. The hamming result (zero advantage) was important but predictable from theory — hamming distance ≠ graph distance for a permutation puzzle. The MLP training + evaluation is the critical experiment.

2. **Profile beam search wall-clock time vs depth** at multiple beam widths to map the feasibility frontier. This would tell us exactly which bucket each beam_width can solve within time budgets.

3. **Access the actual top-solver notebooks** from Kaggle (the ones with 51 votes and 20 votes) — these might contain actual model architectures and beam parameter insights.

4. **Investigate the `graph.random_walks()` depth distribution** — what depth of walks produces training data that generalizes to depth-500+ puzzles?

## 6. Specific experiments to run?

### EXP-A: Trained MLP Predictor Baseline (CRITICAL — run first)
```
1. Generate 100k random walks from solved state, depths 10-50
2. Train 3-layer MLP (120→256→128→1) for 10 epochs, MSE loss
3. Compare beam_search with trained predictor vs unguided at beam_width=4096
   across proxy puzzles (short, medium, hard buckets)
4. Record: per-puzzle path length, solve rate, wall-clock time
```
Expected time: 10-15 minutes on GPU.

### EXP-B: Trained Predictor Depth Generalization (CRITICAL)
```
1. Train predictors on single-depth distributions (depth=10, 20, 50)
2. Evaluate each on puzzles across ALL depth ranges
3. Measure: does depth-matched training generalize? Is domain randomization needed?
```
This answers whether the approach is fundamentally limited.

### EXP-C: Beam Width Feasibility Frontier (MEDIUM)
```
1. For each bucket (short, medium, hard), time beam_search at bw=1024, 4096, 16384, 65536
2. Find the minimum bw that solves ≥80% of bucket puzzles within 10s/puzzle
3. This maps which buckets are solvable with unguided beam search
```

### EXP-D: Two-Phase / Subgroup Reduction (LONGER-TERM)
```
1. Investigate whether Megaminx has a subgroup structure (like Kociemba's cube reduction)
2. If a depth-reducing subgroup exists, a two-phase approach could dramatically reduce beam width needs
```

## 7. What surprised you?

- **Hamming is exactly as bad as unguided**: I expected at least marginal improvement. The fact that they produce identical path lengths at every tested beam width was striking and confirms the predictor must learn actual graph distance.
- **MITM is completely useless for this problem**: BFS diameter 5-6 already produces 1.4M-19M states but only covers depth ≤ 12. The competition is depth 10-1000. MITM is not a factor.
- **`beam_mode='advanced'` has a path-return bug**: This is a critical cayleypy bug. Advanced mode finds the path but can't return it. Simple mode is required.
- **The hamming notebook uses beam_width=65536**: This is 16-32x larger than gen001's maximum. Even so, the notebook only shows results on the first 50 puzzles (depth 1-50). The very_hard bucket (depth 500-1000) is untouched by the public notebooks.

## 8. Helper tools feedback

### `cayleypy_beam_solver` in helpers/core.py
- **Problem 1**: Does not expose `predictor` kwarg. Agents must call cayleypy API directly, which is non-discoverable.
- **Problem 2**: Does not expose `beam_mode` kwarg. Agents default to `simple` mode but can't try `advanced` for speed.
- **Problem 3**: Creates graph without `dtype=torch.int8` — may be using more memory than needed.
- **Problem 4**: Returns None for unsolved puzzles but doesn't distinguish "search failed" vs "search not attempted". Agents can't diagnose failure modes.
- **Recommendation**: Add `predictor`, `beam_mode`, and `dtype` parameters. Document that `simple` mode is required to get paths.

### `Predictor(graph, 'hamming')` API
- Works as documented
- The second argument is `models_or_heuristics` (not just a string)
- Available heuristics: `'hamming'`
- For MLP: pass a trained `torch.nn.Module`

## 9. Time budget

**Sufficient for research but NOT for experiments.** I had 1800s (30 min) and spent:
- 10 min: fetching/analyzing notebooks
- 10 min: running controlled experiments
- 5 min: MITM experiments
- 5 min: writing report

I did NOT have time to train an MLP and measure its beam search quality. This is the single most critical experiment and it couldn't fit in the budget. The recommendation is to either:
(a) Give research agents 3600s (60 min) specifically for running at least ONE ML experiment
(b) Use the experimentator role (not research) for ML experiments — they're designed for running code, not just research

The hamming predictor finding (zero advantage) is valuable but was predictable from first principles. The MLP training experiment is the one that actually advances the pipeline.
