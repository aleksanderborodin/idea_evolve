## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` → C = 1.5028628689
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/exploit_2/sol01.py` → C = 1.5028628703

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/feedback/system_recommendations.md` — Priority 2 describes exactly what to build
- `/home/sasha/Desktop/project_alpha/alpha-evolve/feedback/experiment_suggestions/gen007.md` — bottom section has full API spec
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py` — you will depend on this
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — reference for float64 convention
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/cross_convolution_f64.py` — autoconvolve() returns compatible format
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen007/exploit_1.md` — most successful coord descent run (6551 improvements)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen007/exploit_2.md` — shows convergence at fewer rounds
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/explore_1/sol01.py` — current best, use for testing

## Directive

**Build the `coordinate_descent.py` shared helper.** This has been requested by 4+ agents across gens 6-7 and is the most-requested deliverable in the pipeline. The 40x improvement count discrepancy in gen 7 (6551 vs 156 vs 257 from the same starting point) is caused entirely by non-standardized delta grids.

Implement two functions:

### `coordinate_descent_round(f, autoconv, dx, M, delta_grid=None)`
One full-array pass of coordinate descent using `incremental_autoconv_update`.
- For each element i in f (nonzero elements only by default):
  - Try each delta in `delta_grid`
  - Accept the best delta that reduces C (using incremental autoconv update, NOT FFT)
  - If accepted, update f[i] and autoconv in-place
- Return: `(f_new, autoconv_new, n_improvements, new_c)`

### `run_coordinate_descent(f, n_rounds=10, delta_grid=None, verbose=True)`
Convenience wrapper: initialize autoconv via `autoconvolve()` from cross_convolution_f64, run n_rounds, stop early if 0 improvements in a round.
- Return: `(f_final, total_improvements, c_history)`

### Standard delta grid (from exploit_1 gen 7, most successful run):
```python
DEFAULT_DELTA_GRID = []
for e in range(-12, -1):  # 1e-12 to 1e-2
    DEFAULT_DELTA_GRID.extend([10**e, -(10**e)])
# Proportional deltas added per-element inside the loop:
# [±0.0001, ±0.001, ±0.01, ±0.1] * f[i]
# Zeroing: try f[i]=0 for elements < 1e-6
```

### Critical implementation details:
- Use `from helpers.incremental_autoconv_update import incremental_update` for O(N) updates
- Use `from helpers.cross_convolution_f64 import autoconvolve` for initialization
- Use `from helpers.compute_c_f64 import compute_c_f64` for verification
- Non-negativity: clamp `f[i] + delta` to >= 0, skip if result < 0
- Track max of autoconv correctly: after each accepted move, the max may shift. Use full max recomputation every 100 accepts, incremental tracking otherwise.
- ALL arithmetic in float64

### Testing:
- Load `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/explore_1/sol01.py` (current best, C=1.5028628689)
- Run 1 round of `coordinate_descent_round` — should find 0 or very few improvements (coord descent is converged on this array)
- Load a less-optimized array (e.g., `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen004/research_1/sol01.py`, C=1.5029) — should find hundreds of improvements
- Verify that `run_coordinate_descent` on the less-optimized array converges within 5 rounds
- Verify output C matches `compute_c_f64` to within 1e-12

### Secondary task: Update `helpers/README.md`
The README still says "none yet" for experimentator-created helpers. Update it to document ALL 7 deployed helpers: compute_c_f64, sensitivity, inv_softplus, interpolation, incremental_autoconv_update, cross_convolution_f64, lp_matrix — plus your new coordinate_descent. Include import syntax, function signatures, and brief usage notes for each.

Write all output to `output/helpers/coordinate_descent.py` and `output/helpers/README.md`.
Write `output/report.md` when done.
