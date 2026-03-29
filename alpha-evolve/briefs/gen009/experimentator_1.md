## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen008/explore_1/sol01.py` → C = 1.5028628684790137

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md` — Current helpers index (OUTDATED — shows "none yet" for experimentator helpers)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py` — Key helper to understand for batch evaluator
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/cross_convolution_f64.py` — Autoconvolution computation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — C computation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/core.py` — Built-in JAX helper
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/sensitivity.py` — Sensitivity helper
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/inv_softplus.py` — Inverse softplus helper
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/interpolation.py` — Interpolation helper
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/lp_matrix.py` — LP matrix helper
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_001.md` — Optimization technique overview
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen008/explore_1.md` — Current quadruplet implementation (~112 trials/s bottleneck)

## Directive

**Two deliverables, in this priority order:**

### Deliverable 1: Vectorized Batch Trial Evaluator (PRIMARY)

Build `output/helpers/batch_trial_evaluator.py` with:

```python
def batch_predict_c(autoconv, f_padded, dx, M_fft, indices_batch, deltas_batch):
    """
    First-order prediction of C for K candidate moves simultaneously.

    Args:
        autoconv: (M,) float64 array — current autoconvolution
        f_padded: (M,) float64 array — current zero-padded function
        dx: float — grid spacing
        M_fft: int — FFT length
        indices_batch: (K, k) int array — index sets for each candidate (k=3 for triplets, 4 for quadruplets, etc.)
        deltas_batch: (K, k) float64 array — delta values (must satisfy row-sum ≈ 0)

    Returns:
        (K,) float64 array of predicted new C values

    Uses linear approximation:
        For each candidate j with indices [i1,...,ik] and deltas [d1,...,dk]:
        delta_autoconv[m] += dx * sum(d_p * f_padded[(m - i_p) % M] for p in 1..k)
        (plus second-order cross terms between the k elements)
        new_max = max(autoconv + delta_autoconv)
        new_integral = old_integral + sum(deltas) * dx  (should be ≈ 0 for integral-preserving moves)
        predicted_C = new_max / new_integral^2
    """
```

**Required tests (write in `output/sandbox/`):**
1. Single-candidate output matches `incremental_update` applied sequentially to <1e-8 relative error
2. K=100 batch: all within 1e-6 relative of individual calls
3. Speed benchmark: K=100 candidates at N=30000 should complete in <0.1s (vs ~1s for 100 sequential calls)

**Implementation guidance:**
- The key insight is that `delta_autoconv[m]` for a k-element move is a sum of k circular shifts of f_padded weighted by the deltas. This is vectorizable with numpy fancy indexing.
- For K candidates simultaneously: build a (K, M) matrix of delta_autoconv predictions, take row-wise max, compute predicted C.
- Memory: (K, M) at K=100, M=60000 ≈ 48MB float64. This is fine.
- The approximation is first-order (linear in deltas). For small deltas (~1e-6 to 1e-3), this is accurate. For larger deltas, use it as a filter (keep top 5-10% of candidates for exact evaluation).

### Deliverable 2: Update helpers/README.md

The current README says "none yet" for experimentator-created helpers. There are actually 7 deployed helpers. Write `output/helpers/README.md` documenting ALL helpers with their function signatures:

1. `core.py` — `compute_c(f_values)` → float (JAX, differentiable)
2. `compute_c_f64.py` — `compute_c(f, n_fft_pad=None)` → float (numpy float64)
3. `cross_convolution_f64.py` — `autoconvolve(f)` → (autoconv, f_padded, dx, M_fft)
4. `incremental_autoconv_update.py` — `incremental_update(autoconv, f_padded, idx, delta, dx, M)` → new_autoconv
5. `lp_matrix.py` — `scipy_lp_solve(autoconv, f_padded, tight_idx, dx, M)` → result
6. `interpolation.py` — `interpolate_sparse(f, n_new)` → interpolated array
7. `inv_softplus.py` — `inv_softplus(y, clip_min=...)` → array
8. `sensitivity.py` — gradient/sensitivity computation

Read each helper file to get the exact function signatures and docstrings. Be accurate.

**Important notes on existing helpers:**
- `incremental_update` does NOT modify arrays in place — it returns a new autoconv array. Caller must update f_padded[idx] += delta separately.
- `lp_matrix.py` docstring may be misleading about t<0 indicator — t is constrained ≥0; always use line search regardless of predicted_improvement.
- `coordinate_descent.py` was built in gen 8 but NOT deployed (validation incomplete). Do NOT include it in the README.
