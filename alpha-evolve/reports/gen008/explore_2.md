# Debrief Report — gen008 explore_2

## 1. What did you try?

### Experiment A: LP Plateau Analysis

**Step 1 — Naive downsampling approach (failed):**
Used `interpolate_sparse` to downsample f_30k to N=5000, 8000, 10000, then measured tight
constraint counts. Result: C = 3-7 at all intermediate resolutions (terrible quality).
Tight constraints = 1 at all epsilon levels. LP called scipy_lp_solve — returned t=0 but
line search showed no improvement. Delta applied directly made C much worse.

**Step 2 — Optimized N=5000 approach (partial success):**
Ran coord descent with O(N) incremental autoconv updates at N=5000 starting from the
downsampled array. In 2 minutes, got C=1.679 (far from 1.503 frontier). Tight constraints
throughout: @1e-4 = 3-11, @1e-5 = 1-3. LP at C=1.679 found improvement of -1.04e-8
(tiny but confirms LP is mechanically feasible at N=5000).

### Experiment B: FFT Padding Validation

Computed C with 4 padding sizes: 2N (validate.py standard), 2N-1, next_pow2, 4N. All
gave identical C to within 1e-15. System critic's open question definitively resolved.

## 2. What information did you lack?

- How long does Adam/smooth-max take to optimize at N=5000? I needed a near-optimal N=5000
  solution but couldn't produce one — the gradient approach from initial_programs/ might
  take 10-30 minutes to reach C~1.503.
- The structure of AlphaEvolve N=600 solution at higher resolution: might have been a
  better warm start for N=5000 optimization than the downsampled N=30k.

## 3. What given facts might be wrong or outdated?

- **fact_002 / description.md**: Target C ≤ 1.5053. Already beaten since gen 3. Should be
  updated to reflect current SOTA C = 1.5029.
- **pattern_013**: "~6500 near-max points" at N=30k. Actually tight@1e-7 = 6711, but
  tight@1e-4 = 18325 and tight@1e-5 = 16185. The pattern should specify the epsilon level.
- **State of Affairs ("LP at N=2000 downsampled: direction doesn't transfer")**: This was
  about a different failure mode. The N=2000 case transferred poorly because the resolution
  gap was too large. But the issue at N=5000-10000 is different: the downsampled solution
  has wrong structure (C=7). Not the same problem.

## 4. Was the State of Affairs accurate?

Yes, largely accurate. The note "LP at N=5000-10000: plateau size unknown at these
resolutions. Diagnostic needed before attempting." was correct — the diagnostic was needed
because the naive approach (just downsample) doesn't give useful data.

One gap: the State of Affairs didn't warn that downsampling from N=30k would produce
terrible solutions (C=3-7). The assumption was that interpolation would preserve C near
1.503. It doesn't — the fine structure at N=30k doesn't downsample cleanly.

## 5. What would you do differently with more or different context?

For the LP plateau analysis, the right protocol is:
1. Run Adam + smooth-max optimization at N=5000 from scratch (same as initial_programs/)
   but with N=5000. This would reach C~1.509 basin in minutes, then coord descent to C~1.503.
2. Alternatively, use the AlphaEvolve 600-element solution as a starting point and upsample
   to N=5000, then optimize.

For the FFT padding validation: no changes needed — it's complete and conclusive.

## 6. Specific experiments to run?

### High priority: Near-optimal N=5000 solution

**Protocol:**
1. Initialize with random smooth function at N=5000 (or upsample AlphaEvolve N=600 array)
2. Run Adam + smooth-max gradient descent to reach C~1.509 basin
3. Run coord descent to convergence (C~1.503)
4. Measure tight constraints: @1e-4, @1e-5, @1e-6, @1e-7
5. If tight@1e-5 < 500: run LP, apply line search, record result

This properly answers the LP plateau question. Estimated time: 30-60 minutes.

### Secondary: Triplet perturbation at N=5000

At C=1.679 with coord-descent-converged N=5000 array: are triplet moves effective?
If so, could explore at low N quickly, then upsample successful directions.

## 7. What surprised you?

1. **Downsampling destroys C**: interpolate_sparse reduces C=1.503 → C=7+ at N=5000.
   I expected it to produce C~1.51 or so (similar scale). The function's fine structure
   (many near-zero values between support regions) interpolates poorly.

2. **Very few tight constraints throughout N=5000 optimization**: Even at C=1.68, only
   1-11 tight@1e-4. This is dramatically different from N=30k where tight@1e-4 = 18325
   at C=1.503. This is not just a resolution scaling — the density of tight constraints
   (fraction of autoconv points) is: 0.03-0.11% at N=5000 vs 30.5% at N=30k. If this
   pattern holds near-optimal, LP would be very tractable at N=5000.

3. **FFT padding: perfectly identical results** across all tested padding sizes. No
   numerical discrepancy at all (differences < 1e-15). I expected at least 1e-12
   differences from rounding in different FFT sizes.

4. **LP found a direction at C=1.679**: Even far from optimal, LP found t=0 and line
   search improved by -1e-8. Shows LP formulation is working.

## 8. Helper tools feedback

**Used helpers:** `cross_convolution_f64` (tight_constraint_indices, autoconvolve),
`compute_c_f64`, `interpolation` (interpolate_sparse), `lp_matrix` (scipy_lp_solve),
`incremental_autoconv_update` (incremental_update).

**Bug found:** `incremental_update` function is exported as `incremental_update` but
I initially imported it as `incremental_update_autoconv`. The README.md says it's
`incremental_autoconv_update.py` but doesn't show the actual function name. The
README should show `from helpers.incremental_autoconv_update import incremental_update`.

**Docstring issue:** `scipy_lp_solve` docstring says "If the optimal t < 0, the LP found
an improving direction." But t is constrained to be ≥ 0 by construction (line `bounds.append((0.0, None))`). The actual indicator is: if t=0, the constraints are satisfiable
with improvement epsilon; `predicted_improvement = -t = 0` can be misleading — it looks
like "no improvement" but actually means "improvement of at least epsilon is guaranteed."
The returned delta should be checked via line search regardless of predicted_improvement.

**Missing helper:** `init_smooth_f(N)` — initialize a smooth, near-feasible starting
array for optimization at given N. Would enable faster testing at different resolutions
without running full gradient descent first.

## Key deliverable for future generations

**Experiment B is COMPLETE and DEFINITIVE:**
> All FFT padding sizes (2N-1, 2N, next_pow2, 4N) give C = 1.50286286889246 ± 1e-15.
> The -1e-8 to -1e-9 improvements from coord descent / triplet perturbation are REAL.

**Experiment A finding:**
> Downsampling N=30k → N=5000 gives C=7+ (not near-optimal). Cannot answer LP plateau
> question with this approach. Need fresh optimization at N=5000 from scratch. Tight
> constraint density at N=5000 is dramatically lower than N=30k (by ~300x), suggesting
> LP may be tractable at near-optimal N=5000 — but this needs proper initialization.
