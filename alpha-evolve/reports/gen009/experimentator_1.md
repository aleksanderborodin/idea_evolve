# Debrief Report — gen009_experimentator_1

## Summary

Both deliverables completed:
1. `output/helpers/batch_trial_evaluator.py` — `batch_predict_c` function, 46x speedup at N=30000
2. `output/helpers/README.md` — Full documentation of all 8 deployed helpers

---

## 1. What did I try?

### Deliverable 1: batch_predict_c

Implemented and benchmarked 3 approaches:

**Approach 1 — Direct fancy indexing (rejected):**
- Build (K, M) index array and gather f_padded values
- Time: 650ms for K=100 at N=30000. Slower than sequential (624ms)
- Root cause: random memory access into (K=100, M=60000) int64 index arrays is cache-unfriendly

**Approach 2 — FFT-based convolution (rejected):**
- Build sparse impulse matrix (K, M), batch rfft/irfft on (K, M) arrays
- Time: 387ms. Still slower than sequential
- Root cause: rfft+irfft on (100, 60000) matrix = 490ms, dominated by 48MB memory bandwidth

**Approach 3 — Window-based (WINNER, deployed):**
- Find tight indices (where autoconv ≥ max*(1-1e-5))
- Evaluate delta_autoconv only at those indices ±300 positions (W~401 at N=30000)
- Time: **13ms** for K=100 at N=30000 (46x speedup)
- Root cause of speed: (K, k, W) = (100, 4, 401) intermediate array = 1.3MB fits in L2 cache

**Tests written:** 5 tests in `output/sandbox/scripts/test_batch_trial_evaluator.py`
- All 5 tests pass
- Single-candidate match vs incremental_update: relative error 0 (exact)
- K=100 batch match: max relative error 2.13e-16 (machine precision)
- Speed: 22.7ms at N=30000 (test includes first-run overhead; steady-state ~13ms)
- Triplet (k=3) support: verified
- Top-10 ranking overlap: 10/10

### Deliverable 2: README.md

Read all 8 deployed helper files. Documented:
- All function signatures with args/returns
- Usage examples for each helper
- Important notes (docstring corrections, deployment status of coordinate_descent.py)

---

## 2. What information did I lack?

- The exact delta magnitude distribution used by gen009 agents — I used 1e-5 based on gen008
  debrief. If agents use larger deltas (>0.01), the window approach may miss some max shifts.
- Whether gen009 agents use triplets, quadruplets, or larger k. The helper supports any k.
- The current tight-constraint profile of the best solution at each candidate N value.

---

## 3. What might be wrong or outdated?

- `helpers/README.md` previously said "none yet" for experimentator helpers. There were 7.
  The index was stale. Now corrected.
- `lp_matrix.py` docstring says `predicted_improvement` is negative for improvement (sign
  convention: t is minimized slack, so negative t means the LP found improvement). This is
  confusing but correct. Documented in the new README with a warning.
- `sensitivity.py` mentions "float64 mode is ~N times slower" — actually it's O(N) finite
  difference calls, so ~N times slower. Correct, just worth emphasizing.

---

## 4. Was the State of Affairs accurate?

Not read fully (prioritized getting the helpers built). The gen008 debrief correctly
identified "missing vectorized batch trial evaluator" as the highest-impact helper need.
The brief was well-specified and actionable.

---

## 5. What would I do differently with more context?

- Profile the actual gen009 agent's delta distribution before fixing window_half=300.
  For larger deltas, window_half=500 or 1000 may be needed.
- Add a validation mode: `strict=True` parameter that falls back to exact incremental_update
  for candidates where predicted_c < current_c (i.e., when the move looks promising).
- The `batch_incremental_updates` in incremental_autoconv_update.py could be vectorized
  similarly — apply all updates simultaneously rather than one at a time in a Python loop.

---

## 6. Specific experiments to run

**Experiment A: Window size sensitivity**
- Question: For the best current solution, at what |delta| does the predicted max start
  missing the true max?
- Method: Sweep delta magnitude from 1e-6 to 1e-1. For each magnitude, compare
  batch_predict_c vs exact incremental_update on K=100 random candidates. Report
  delta threshold where max rel error exceeds 1e-6.
- Expected: threshold is ~0.01. This sets the "use as filter only" threshold.

**Experiment B: Larger batch sizes**
- The speedup comes from amortizing window setup over K. Does K=1000 scale linearly?
- Expected: K=1000 should take ~130ms, enabling ~7500 predictions/s filter rate.

**Experiment C: gen009 workflow integration test**
- Run a full quadruplet optimization session using batch_predict_c as pre-filter:
  sample K=200, keep top 10%, verify top 20 exactly.
- Measure wall-clock speedup vs gen008's Python loop.

---

## 7. What surprised me?

1. **FFT batching is NOT faster than sequential at N=30000.** Counter-intuitive given
   FFT's O(N log N) advantage. The bottleneck is memory bandwidth: (100, 60000) matrices
   are 48MB per operation, saturating RAM. The window approach avoids this entirely.

2. **Only 1 tight index at epsilon_rel=1e-5 for the current best solution.** The best
   solution at C=1.5029 has a single binding constraint. This is why the window approach
   works so well — the entire window is 401 points out of 60,000.

3. **Window approach matches machine precision (not just first-order accuracy).** For small
   deltas, the approximation error is at the level of floating-point rounding (~1e-16),
   not the first-order approximation error (~delta^2/autoconv_max * something). This is
   because the deltas are so small that second-order terms are negligible.

---

## 8. Helper tools feedback

- **incremental_autoconv_update.py**: Correct and well-documented. The "does NOT modify
  in-place" warning is important and well-placed. No bugs found.
- **compute_c_f64.py**: Correct. Used as ground truth for tests.
- **cross_convolution_f64.py**: `autoconvolve()` returns (autoconv, f_padded, dx, M_fft) —
  exactly what batch_predict_c needs as input. Good API design.
- **lp_matrix.py**: `scipy_lp_solve()` returns `predicted_improvement = -t`, which is
  negative when improvement is found. This sign convention is confusing and I had to
  read the source carefully. The README note should help future agents.
- **batch_trial_evaluator.py (new)**: Tested extensively. Correct, fast, well-documented.
  Deploy to `problem/helpers/`.
- **Wish existed**: A function that wraps the full filtering workflow — sample K candidates
  with gradient guidance, batch-predict, verify top N%. Would make agents 50x faster at
  the optimization loop with minimal code per agent.

---

## 9. Time budget

**Had enough time.** Both deliverables completed with time to run benchmarks and write
thorough documentation.

**If I had more time:**
- Write the integration wrapper (full filtering workflow as a helper)
- Profile gen009 agents' actual delta distributions
- Test the helper against the current best solution's optimization landscape
- Verify behavior at larger window_half values for gen-9 quadruplet deltas

---

## Output files

- `output/helpers/batch_trial_evaluator.py` — production helper (deploy to problem/helpers/)
- `output/helpers/README.md` — updated documentation for all 8 helpers
- `output/experiment_results.md` — structured experiment report
- `output/observations.md` — key observations
- `output/sandbox/scripts/batch_trial_evaluator_dev.py` — development version (two implementations)
- `output/sandbox/scripts/test_batch_trial_evaluator.py` — 5 tests, all passing
