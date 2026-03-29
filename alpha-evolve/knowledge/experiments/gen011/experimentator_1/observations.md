# Observations — experimentator_1, Generation 11

## Key findings

1. **The three gen 10 CD optimizations package cleanly into a single helper.** Top-K screening, FFT resync, and geometric delta grid are complementary with no conflicts. The combined helper is ~250 lines including docstrings and edge case handling.

2. **Inline incremental update is bit-identical to the helper.** `np.max(np.abs(inline - helper)) = 0.0`. No numerical divergence from operation ordering.

3. **Top-K screening guarantees no false negatives** because it checks a subset of autoconv positions. If the subset max already >= best_C, the true max (over all positions) must be >= best_C too. This is a one-sided guarantee: it can have false positives (subset suggests improvement but full check rejects) but never false negatives.

4. **`problem/helpers/README.md` is severely outdated** — says no experimentator-created helpers exist, but there are 10. Updated version provided in `output/helpers/README.md`.

5. **`knowledge/alphaevolve_reference_arrays.py` is broken** — has top-level `print(f"Score: {evaluate_sequence(best_sequence)}")` where `evaluate_sequence` is undefined. Cannot be imported.
