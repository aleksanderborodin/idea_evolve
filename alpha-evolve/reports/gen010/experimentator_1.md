# Experimentator 1 — Gen 10 Debrief

## What did I try?

Built and validated the `plateau_analyzer` helper (Priority 7 from system recommendations).

**Deliverables completed:**
1. `output/helpers/plateau_analyzer.py` — `plateau_analysis()` function that finds near-max
   autoconvolution positions and computes exact per-element gradients at each.
2. `output/sandbox/scripts/test_plateau_analyzer.py` — 8 comprehensive tests covering
   gradient correctness (finite differences), C consistency, threshold behavior, performance,
   pre-computed autoconv, constant function, gradient shape, and real solution.
3. `output/helpers/README.md` — Updated helpers README documenting ALL 10 helpers (was
   previously saying "none yet" for experimentator-created helpers despite 8 existing ones).

**All 8 tests passed.** Key metrics:
- Gradient max absolute error: 2.39e-10 (vs 1e-8 tolerance)
- C consistency: exact match with compute_c_f64
- Performance: 6.7ms median at N=30000 (budget was 100ms)

## What information did I lack?

- Could not test with the actual current best solution because `best.py` runs a live
  optimization (imports a base solution then perturbs it) rather than returning a static
  array. Would have been useful to verify the K=13 plateau positions reported by gen 9
  exploit_1 directly.

## What given facts might be wrong or outdated?

- The brief states "13 plateau positions within 1e-12 of max" from gen 9 exploit_1's report.
  This is likely still accurate for that specific solution but K may differ for solutions
  produced in gen 10.

## Was the State of Affairs accurate?

Did not identify any inaccuracies relevant to this task.

## What would I do differently with more context?

- If I had a static `.npy` checkpoint of the best solution, I could have verified the
  plateau structure directly and tested gradient-based minimax perturbation end-to-end.

## Specific experiments to run

1. **Minimax LP integration test:** Use plateau_analysis output with scipy.optimize.linprog
   to find a perturbation that reduces max across all K plateau positions. Verify the LP
   is feasible and the resulting perturbation actually reduces C.
2. **Gradient linear dependence check:** At the current best solution, check rank of the
   K×N gradient matrix. If rank < K, the minimax LP may have limited feasibility.
3. **Plateau stability under perturbation:** After applying a minimax perturbation, re-run
   plateau_analysis and check whether new plateau positions appear (the "whack-a-mole" effect).

## What surprised me?

- Performance was much better than expected: 6.7ms vs 100ms budget. The bottleneck is
  FFT computation of autoconv (when not pre-supplied), not the gradient matrix construction.
  When autoconv is pre-supplied (as it would be in an optimization loop), the function is
  essentially just a vectorized array lookup.
- The gradient formula is remarkably simple: `2 * dx * f_padded[(n - m) % M]`. This is
  because autoconvolution uses f twice, so the derivative has a factor of 2.

## Helper tools feedback

- **compute_c_f64:** Used for consistency verification. Correct and well-documented.
- **incremental_autoconv_update:** Read for reference on the autoconv data structure
  conventions (f_padded, dx, M_fft). Conventions are consistent across all helpers.
- **batch_trial_evaluator:** Read as an example of well-structured helper code. Good model.
- The helpers README was significantly outdated — it listed "none yet" for experimentator
  helpers despite 8 deployed helpers. Fixed in deliverable 3.

## Time budget

Had sufficient time. All three deliverables completed and tested. If more time were
available, I would have:
1. Implemented a proof-of-concept minimax LP solver using the plateau_analysis output
2. Tested with a static version of the current best solution
3. Profiled memory usage of the (K, N) gradient matrix at large K values
