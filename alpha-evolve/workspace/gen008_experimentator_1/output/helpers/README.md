# Problem Helpers

All reusable helpers live here. Import them in solution files as:

    from helpers.<module> import <function>

`evaluate.py` adds `problem/` to `sys.path`, so `helpers/` is directly importable.

---

## Built-in helpers

### `core.py` — Problem-specific core helper

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_c` | `(f_values: jnp.ndarray) -> float` | JAX-based, differentiable. Computes C = max(f★f) / (∫f)² via FFT. |

Import: `from helpers.core import compute_c`

---

## Experimentator-created helpers

### `compute_c_f64.py` — Float64 C computation

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_c_f64` | `(f_array) -> float` | Float64 compute_c matching validate.py exactly. Use for all accept/reject decisions. |

Import: `from helpers.compute_c_f64 import compute_c_f64`

### `sensitivity.py` — Gradient / sensitivity analysis

| Function | Signature | Description |
|----------|-----------|-------------|
| `sensitivity_map` | `(f_array, use_float64=False) -> array` | Compute dC/df[i] for all elements. Float32 JAX autodiff or float64 finite differences. |

Import: `from helpers.sensitivity import sensitivity_map`

### `inv_softplus.py` — Safe inverse softplus

| Function | Signature | Description |
|----------|-----------|-------------|
| `inv_softplus_safe` | `(f, eps=1e-8, clip_min=-10.0, clip_max=30.0) -> array` | Convert non-negative values to raw params for softplus warm-start optimization. |

Import: `from helpers.inv_softplus import inv_softplus_safe`

### `interpolation.py` — Structure-preserving interpolation

| Function | Signature | Description |
|----------|-----------|-------------|
| `interpolate_sparse` | `(array, target_n, threshold=1e-4) -> array` | Upsample/downsample preserving near-zero regions as exact zeros. |

Import: `from helpers.interpolation import interpolate_sparse`

### `incremental_autoconv_update.py` — O(N) incremental autoconvolution

| Function | Signature | Description |
|----------|-----------|-------------|
| `incremental_update` | `(autoconv, f_padded, idx, delta, dx, M_fft) -> array` | Update autoconv when f[idx] changes by delta. O(N) instead of O(N log N). |
| `batch_incremental_updates` | `(autoconv, f_padded, indices, deltas, dx, M_fft) -> (autoconv, f_padded)` | Apply multiple updates sequentially (modifies in-place). |

Import: `from helpers.incremental_autoconv_update import incremental_update`

### `cross_convolution_f64.py` — Float64 cross-convolution and autoconvolution

| Function | Signature | Description |
|----------|-----------|-------------|
| `cross_convolve` | `(f, g, dx=None) -> array` | Compute (f★g) via FFT in float64. Returns length 2N-1. |
| `autoconvolve` | `(f, dx=None) -> (autoconv, f_padded, dx, M_fft)` | Compute (f★f) in float64, returns full M=2N array compatible with incremental_update. |
| `tight_constraint_indices` | `(f, epsilon_rel=1e-5) -> array` | Find indices where autoconv is within epsilon of max. |

Import: `from helpers.cross_convolution_f64 import autoconvolve, tight_constraint_indices`

### `lp_matrix.py` — LP constraint matrix builder

| Function | Signature | Description |
|----------|-----------|-------------|
| `build_lp_matrix` | `(f, tight_indices, dx=None) -> (A_ub, M_fft, f_padded)` | Build linearized LP constraint matrix for autocorrelation refinement. |
| `build_lp_rhs` | `(autoconv, tight_indices, epsilon=0.0) -> (b_ub, A_max)` | Build LP right-hand side vector. |
| `scipy_lp_solve` | `(f, tight_indices, autoconv, ...) -> dict` | Solve the linearized LP to find an improving perturbation. |

Import: `from helpers.lp_matrix import build_lp_matrix, scipy_lp_solve`

### `coordinate_descent.py` — Standardized coordinate descent optimizer

| Function | Signature | Description |
|----------|-----------|-------------|
| `coordinate_descent_round` | `(f, autoconv, dx, M_fft, ...) -> (f_new, autoconv_new, n_improvements, new_c)` | One full-array pass. Uses hot-set screening + full-max verification. ~147s for N=30k. |
| `run_coordinate_descent` | `(f, n_rounds=10, ...) -> (f_final, total_improvements, c_history)` | Multi-round wrapper with auto-initialization, early stopping, and FFT verification. |

Import: `from helpers.coordinate_descent import run_coordinate_descent, coordinate_descent_round`

**Standard delta grid:** ±1e-12 through ±1e-2 (absolute) + ±0.01% through ±10% (proportional per element). Matches exploit_1 gen 7 (6551 improvements).

---

## How helpers are added

Experimentator agents write helpers to `output/helpers/<name>.py`. The orchestrator:
1. Validates syntax, checks import blocklist, verifies no top-level side effects.
2. Deploys the file here as `problem/helpers/<name>.py`.
3. Updates this README and the orchestrator's `_helpers_section()` prompt.

Do **not** add files directly to this directory — always go through the experimentator workflow.
