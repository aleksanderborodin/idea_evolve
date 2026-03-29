## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` → C = 1.5028628689
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/exploit_2/sol01.py` → C = 1.5028628703

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_003.md` — LP status and remaining angles
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/explore_1/sol01.py` — current best (for plateau analysis)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen007/full_1.md` — LP failure details and plateau characterization
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/cross_convolution_f64.py` — autoconvolve(), tight_constraint_indices()
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — float64 C computation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/interpolation.py` — interpolate_sparse for downsampling
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/lp_matrix.py` — LP matrix construction + scipy_lp_solve
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/feedback/experiment_suggestions/gen007.md` — Experiment 4 describes LP plateau analysis

## Directive

**Two diagnostic experiments to provide information for future generations.** This is divergent exploration — solutions are a bonus, not the primary goal.

### Experiment A: LP Plateau Analysis at Intermediate Resolution (PRIMARY)

The LP approach is blocked at N=30k because the autoconvolution has ~6500 near-max points (pattern_013). But the plateau count at N=5000-10000 is unknown. If it's <500, LP becomes tractable.

**Protocol:**
1. Load population/best.py (N=30000, C=1.5028628689)
2. Downsample to N=5000, N=8000, N=10000 using linear interpolation (or take every k-th element and renormalize)
3. For each resolution:
   a. Compute autoconvolution via FFT
   b. Count tight constraint indices at eps=1e-4, 1e-5, 1e-6, 1e-7 using `tight_constraint_indices`
   c. Report: count at each epsilon, and the C value at that resolution
4. **If count < 500 at any resolution with eps=1e-5:**
   a. Attempt LP solve using `scipy_lp_solve` from lp_matrix helper
   b. Apply LP direction with line search at that resolution
   c. If LP improves C at that resolution, upsample the direction to N=30k and test

**Report format (in observations.md):**
```
| N     | C at this N | tight @ 1e-4 | tight @ 1e-5 | tight @ 1e-6 | tight @ 1e-7 |
|-------|-------------|--------------|--------------|--------------|--------------|
| 5000  | ...         | ...          | ...          | ...          | ...          |
| 8000  | ...         | ...          | ...          | ...          | ...          |
| 10000 | ...         | ...          | ...          | ...          | ...          |
| 30000 | ...         | ...          | ...          | ~6500        | ...          |
```

### Experiment B: FFT Padding Validation

The system critic has flagged for 2 generations that improvements of -1e-8 to -1e-9 may be FFT artifacts. No validation has been done.

**Protocol:**
1. Load population/best.py
2. Compute C using validate.py's method (np.fft.rfft with zero-padding to 2N-1)
3. Compute C with alternative padding: 2N, next power of 2, 4N
4. Report: C value at each padding size. If they differ by more than 1e-10, flag it.

This takes <5 minutes and settles an open question that has been unresolved since gen 5.

### If LP finds an improvement at intermediate N:
Bake the improved array as sol01.py. Otherwise, write a diagnostic-only report.

**What NOT to do:**
- Do NOT try LP at N=30k (blocked, 4 failures, pattern_013)
- Do NOT try coordinate descent or triplets (exploit agents are doing that)
- Do NOT spend time on gradient descent approaches
- Begin coding immediately. Do NOT spend more than 3 turns reading files.
