# Observations — gen001_research_1

## Key Observations

1. **The ML pipeline is confirmed working in this environment.** `Puzzles.megaminx()`, `random_walks`, `Predictor`, and `beam_search(predictor=...)` all work. No dependency issues.

2. **cayleypy's `cayleypy_beam_solver` helper does NOT support `predictor` kwarg.** Agents must call `CayleyGraph(Puzzles.megaminx()).beam_search(predictor=...)` directly.

3. **The growth function confirms beam search alone is hopeless for deep puzzles.** Depth 8 = 3.5B states. Even with a predictor guiding the beam, the very_hard bucket (depth 500-1000) is a massive extrapolation problem.

4. **Move cancellation is the easiest immediate win** — 5-15% compression on sample_submission paths with zero search.

5. **MITM with BFS depth 6 covers optimal distances up to 12.** Only helps for `short` bucket (depth 1-25) and possibly some `medium` (depth 26-100).

6. **The RTX 5060 Ti GPU is available but unused by default.** The graph uses CPU unless `device='cuda'` is passed. For ML-guided beam search, GPU evaluation of the predictor matters a lot.

7. **The `Predictor(graph, 'hamming')` built-in** is available as a zero-cost baseline predictor before training a custom model.

8. **kaggle CLI hangs on some notebook pulls.** `lilypilly/cayleypy-cube-train-and-solve-smallmodel` and `fedimser/beam-search-with-cayleypy` could not be fetched. The MITM and ML base notebooks worked fine.

9. **The helper's `PROXY_SIZE` in README is wrong (100 vs 101).** Code and description.md both correctly say 101.

10. **No generation-1 agent outputs exist yet** — all knowledge directories (ideas, clusters, facts) are empty. The State of Affairs correctly identifies this as a fresh start.
