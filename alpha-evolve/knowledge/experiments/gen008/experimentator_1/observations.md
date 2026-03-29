# Observations — experimentator_1, Generation 8

## Task
Build the `coordinate_descent.py` shared helper and update `helpers/README.md`.

## What was done
1. Read all 7 existing helpers to understand APIs and conventions
2. Read exploit_1 and exploit_2 gen7 reports for coord descent implementation details
3. Wrote `coordinate_descent.py` with two functions:
   - `coordinate_descent_round(f, autoconv, dx, M_fft, delta_grid)` — single full-array pass
   - `run_coordinate_descent(f, n_rounds, delta_grid, verbose)` — multi-round convenience wrapper
4. Wrote comprehensive test suite in `sandbox/scripts/test_coordinate_descent.py`
5. Found and fixed a critical bug: initial version compared only `max(autoconv)` for accept/reject, but C = max(autoconv)/integral^2 — the integral also changes with each delta. Fixed to compare full C ratio.
6. Small-array tests (N=500) passed: correctness, non-negativity, verification against compute_c_f64
7. Large-array tests (N=30000) timed out — the O(N) incremental update per delta trial, with ~30 deltas per element and 25k nonzero elements, takes ~85s per round as expected. Tests were running but ran out of session time.

## Status
- `coordinate_descent.py`: Written, small-array tests pass, large-array tests not completed
- `README.md` update: Not completed (ran out of time)
- No solution files produced (this was a helper task, not a solution task)

## Key implementation details
- Uses `incremental_update` from `helpers/incremental_autoconv_update` for O(N) per-delta evaluation
- Delta grid: absolute +-1e-12 to +-1e-2 (22 values) + proportional +-0.01% to +-10% (8 values) + zeroing for small elements
- Accept criterion: full C = max(autoconv)/integral^2, not just max(autoconv)
- Periodic FFT resync every 200 accepts to prevent drift
- Non-negativity enforced: skip deltas that would make f[i] < 0
