# Problem Helpers

All reusable helpers live here. Import them in solution files as:

    from helpers.<module> import <function>

`evaluate.py` adds `problem/` to `sys.path`, so `helpers/` is directly importable.

---

## Built-in helpers

### `core.py` — JAX-based C computation (float32, differentiable)

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_c` | `(f_values: jnp.ndarray) -> float` | JAX-based, differentiable. Computes C = max(f★f) / (∫f)² via FFT. Uses float32. |

Import: `from helpers.core import compute_c`

**Use for:** gradient computation (JAX autodiff), quick sanity checks. **NOT** for accept/reject decisions — float32 is insufficient for micro-optimization (see pattern_008).

---

## Experimentator-created helpers

### `compute_c_f64.py` — Float64 C computation (numpy, matches validate.py)

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_c_f64` | `(f_array) -> float` | Numpy float64, matches validate.py exactly. Returns scalar C. |

Import: `from helpers.compute_c_f64 import compute_c_f64`

**Use for:** all accept/reject decisions in optimization. Float64 precision (~1e-15) is essential for distinguishing improvements at C < 1.505. Raises `ValueError` if array is empty, non-finite, or has near-zero integral.

---

### `sensitivity.py` — Gradient dC/df[i] (float32 JAX or float64 finite diff)

| Function | Signature | Description |
|----------|-----------|-------------|
| `sensitivity_map` | `(f_array, use_float64=False) -> array` | Gradient of C w.r.t. each element. |

Import: `from helpers.sensitivity import sensitivity_map`

**Use for:** identifying which elements have the most impact on C. Two modes:
- `use_float64=False` (default): JAX float32 autodiff, fast (~1s for N=30k). Rankings unreliable for well-optimized solutions.
- `use_float64=True`: Numpy float64 finite differences, slow (O(N) evaluations). Essential for micro-optimization at C < 1.505.

**Warning:** At well-optimized solutions (C < 1.505), float32 gradients misrank elements significantly. Use float64 mode for precise gradient information.

---

### `inv_softplus.py` — Inverse softplus for warm-start optimization

| Function | Signature | Description |
|----------|-----------|-------------|
| `inv_softplus_safe` | `(f, eps=1e-8, clip_min=-10.0, clip_max=30.0) -> array` | Converts non-negative f to raw_params where softplus(raw_params) ≈ f. |

Import: `from helpers.inv_softplus import inv_softplus_safe`

**Use for:** warm-starting JAX gradient descent from an existing solution. Converts a numpy array to softplus parameterization for smooth optimization.

**WARNING — sparse arrays:** Default `clip_min=-10` maps near-zero elements to softplus(-10) ≈ 4.5e-5, making them non-zero. For sparse solutions (many exact zeros), use `clip_min=-20` to preserve sparsity (softplus(-20) ≈ 2e-9). Wrong clip_min inflates the integral by adding many tiny values.

---

### `interpolation.py` — Structure-preserving upsampling/downsampling

| Function | Signature | Description |
|----------|-----------|-------------|
| `interpolate_sparse` | `(array, target_n, threshold=1e-4) -> array` | Resample array to target_n while preserving near-zero regions as exact zeros. |

Import: `from helpers.interpolation import interpolate_sparse`

**Use for:** changing resolution of a solution while preserving its support structure. Standard cubic spline interpolation can fill in zeros with small positive values, inflating the integral; this helper avoids that artifact.

**Example:** Upsampling a 1000-element solution to 30000 elements while keeping zero regions exact zeros.

---

### `incremental_autoconv_update.py` — O(N) autoconvolution update

| Function | Signature | Description |
|----------|-----------|-------------|
| `incremental_update` | `(autoconv, f_padded, idx, delta, dx, M_fft) -> new_autoconv` | Update autoconv when f[idx] += delta, O(N) instead of O(N log N). |
| `batch_incremental_updates` | `(autoconv, f_padded, indices, deltas, dx, M_fft) -> (autoconv, f_padded)` | Apply multiple incremental updates sequentially. Modifies inputs in-place. |

Import: `from helpers.incremental_autoconv_update import incremental_update`

**Use for:** coordinate descent optimization. When testing many single-element perturbations (as in exploit/full agent coordinate descent), this avoids recomputing the full FFT for each candidate. Provides ~28x speedup at N=30000.

**Accuracy:** Max error vs full FFT < 1e-18 (verified on 11 test cases). The formula is:
```
autoconv_new[n] = autoconv_old[n] + dx * (2 * delta * f_padded[(n-idx) % M] + delta^2 * (n == 2*idx))
```

**Important:** Does NOT update f_padded in-place. Caller must do `f_padded[idx] += delta` after calling `incremental_update`. `batch_incremental_updates` DOES update f_padded in-place.

**Setup:** Obtain `autoconv` and `f_padded` via `autoconvolve()` from `cross_convolution_f64.py`:
```python
from helpers.cross_convolution_f64 import autoconvolve
from helpers.incremental_autoconv_update import incremental_update

ac, f_padded, dx, M = autoconvolve(f)
# ... optimization loop ...
new_ac = incremental_update(ac, f_padded, idx, delta, dx, M)
```

---

### `cross_convolution_f64.py` — Float64 cross-convolution and tight constraint analysis

| Function | Signature | Description |
|----------|-----------|-------------|
| `cross_convolve` | `(f, g, dx=None) -> array` | (f★g)(t) via FFT in float64. Returns length 2N-1 array. |
| `autoconvolve` | `(f, dx=None) -> (autoconv, f_padded, dx, M_fft)` | (f★f) in float64. Returns length 2N array + supporting data for incremental updates. |
| `tight_constraint_indices` | `(f, epsilon_rel=1e-5) -> indices` | Find indices j where autoconv[j] ≥ (1 - epsilon_rel) * max_autoconv. |

Import: `from helpers.cross_convolution_f64 import cross_convolve, autoconvolve, tight_constraint_indices`

**Use for:**
- `autoconvolve`: Primary entry point for float64 autoconvolution computation. Returns data in the format needed by `incremental_autoconv_update`.
- `cross_convolve`: Computing (f★g) for two different arrays. Useful for LP constraint matrix columns.
- `tight_constraint_indices`: Identifying near-tight LP constraints. Use `epsilon_rel=1e-6` for tightest constraints (1-3 indices), `epsilon_rel=1e-3` for more.

**Convention:** `autoconvolve` returns an array of length 2N (matching `compute_c_f64` and `incremental_autoconv_update`). `cross_convolve` returns 2N-1 (standard linear convolution length). Use `autoconvolve` when chaining with `incremental_update`.

---

### `lp_matrix.py` — Vectorized LP constraint matrix for autocorrelation refinement

| Function | Signature | Description |
|----------|-----------|-------------|
| `build_lp_matrix` | `(f, tight_indices, dx=None) -> (A_ub, M_fft, f_padded)` | Build constraint matrix A_ub[j,k] = 2*f_padded[(j-k)%M]*dx. Vectorized, no Python loops. |
| `build_lp_rhs` | `(autoconv, tight_indices, epsilon=0.0) -> (b_ub, A_max)` | Build RHS vector b_ub[j] = A_max - autoconv[j] - epsilon. |
| `scipy_lp_solve` | `(f, tight_indices, autoconv, ...) -> result dict` | One-shot LP step: find integral-preserving delta that reduces autoconv at tight indices. |

Import: `from helpers.lp_matrix import build_lp_matrix, build_lp_rhs, scipy_lp_solve`

**Use for:** LP-based refinement of near-optimal solutions. The LP linearizes the autoconvolution constraint around the current solution and finds a descent direction.

**Critical limitation:** The LP only constrains the specified `tight_indices`. A single LP step may increase autoconvolution at non-tight indices, worsening global C. Requires iterative use:
```python
for _ in range(n_iters):
    ac, fp, dx, M = autoconvolve(f)
    tight = tight_constraint_indices(f, epsilon_rel=1e-6)
    result = scipy_lp_solve(f, tight, ac, epsilon=1e-10, max_step=0.01)
    if result['status'] == 0:
        f = np.maximum(f + result['delta'], 0.0)
        # re-evaluate C with compute_c_f64 to verify actual improvement
```

**Scaling guidance (from gen006 full_1 debrief):**
- At N=30000 with n_tight=100: A_ub is 100×30000 = ~24MB, LP solves in seconds.
- Python-loop construction at N=30000 took 19min and 7GB RAM. This vectorized version avoids that.
- Recommended: work at reduced resolution (N=2000-5000), upsample delta via `interpolation.py`.

---

## How helpers are added

Experimentator agents write helpers to `output/helpers/<name>.py`. The orchestrator:
1. Validates syntax, checks import blocklist, verifies no top-level side effects.
2. Deploys the file here as `problem/helpers/<name>.py`.
3. Updates this README and the orchestrator's `_helpers_section()` prompt.

Do **not** add files directly to this directory — always go through the experimentator workflow.
