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

### `compute_c_f64.py` — Float64 compute_c

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_c_f64` | `(f_array) -> float` | NumPy float64 C computation matching validate.py exactly. Precision ~1e-15. Use for accept/reject decisions. |

Import: `from helpers.compute_c_f64 import compute_c_f64`

### `cross_convolution_f64.py` — Cross-convolution and tight-constraint helpers

| Function | Signature | Description |
|----------|-----------|-------------|
| `cross_convolve` | `(f, g, dx=None) -> ndarray` | Float64 cross-convolution (f★g) via FFT. |
| `autoconvolve` | `(f) -> (autoconv, f_padded, dx, M)` | Convenience wrapper for self-convolution with all intermediate arrays. |
| `find_tight_indices` | `(autoconv, epsilon_rel=1e-5) -> ndarray` | Find indices where autoconv is within epsilon_rel of its max. |

Import: `from helpers.cross_convolution_f64 import cross_convolve, autoconvolve, find_tight_indices`

### `incremental_autoconv_update.py` — O(N) incremental autoconvolution update

| Function | Signature | Description |
|----------|-----------|-------------|
| `incremental_update` | `(autoconv, f_padded, idx, delta, dx, M_fft) -> ndarray` | O(N) update when f[idx] changes by delta. ~28x faster than FFT recompute. |
| `batch_incremental_updates` | `(autoconv, f_padded, indices, deltas, dx, M_fft) -> (autoconv, f_padded)` | Apply multiple updates sequentially, modifying arrays in-place. |

Import: `from helpers.incremental_autoconv_update import incremental_update, batch_incremental_updates`

### `batch_trial_evaluator.py` — Vectorized batch trial evaluator

| Function | Signature | Description |
|----------|-----------|-------------|
| `batch_predict_c` | `(autoconv, f_padded, dx, M_fft, indices_batch, deltas_batch, ...) -> ndarray` | First-order prediction of C for K candidate moves simultaneously. 40-80x faster than sequential exact evaluation. |

Import: `from helpers.batch_trial_evaluator import batch_predict_c`

### `lp_matrix.py` — LP constraint matrix builder

| Function | Signature | Description |
|----------|-----------|-------------|
| `build_lp_constraint_matrix` | `(f_padded, tight_indices, dx, M_fft) -> ndarray` | Vectorized LP constraint matrix A_ub for linearized autocorrelation refinement. |
| `scipy_lp_solve` | `(f, autoconv, ...) -> (delta, result)` | Full LP solve: build matrix, set up objective/bounds, call scipy.optimize.linprog. |

Import: `from helpers.lp_matrix import build_lp_constraint_matrix, scipy_lp_solve`

### `sensitivity.py` — Sensitivity analysis

| Function | Signature | Description |
|----------|-----------|-------------|
| `sensitivity_map` | `(f_array, use_float64=False) -> ndarray` | Compute dC/df[i] for all elements. Float32 JAX autodiff (fast) or float64 finite differences (precise). |

Import: `from helpers.sensitivity import sensitivity_map`

### `interpolation.py` — Structure-preserving interpolation

| Function | Signature | Description |
|----------|-----------|-------------|
| `interpolate_sparse` | `(array, target_n, threshold=1e-4) -> ndarray` | Upsample/downsample preserving near-zero structure as exact zeros. |

Import: `from helpers.interpolation import interpolate_sparse`

### `inv_softplus.py` — Safe inverse softplus

| Function | Signature | Description |
|----------|-----------|-------------|
| `inv_softplus_safe` | `(f, eps=1e-8, clip_min=-10.0, clip_max=30.0) -> ndarray` | Convert non-negative values to softplus raw_params for warm-start optimization. |

Import: `from helpers.inv_softplus import inv_softplus_safe`

### `plateau_analyzer.py` — Autoconvolution plateau structure analyzer

| Function | Signature | Description |
|----------|-----------|-------------|
| `plateau_analysis` | `(f, autoconv=None, threshold_rel=1e-12) -> dict` | Find near-max autoconv positions and compute per-element gradients at each. Returns positions, values, gradients (K,N), max_val, max_idx. For minimax perturbation (idea_023). |

Import: `from helpers.plateau_analyzer import plateau_analysis`

---

## How helpers are added

Experimentator agents write helpers to `output/helpers/<name>.py`. The orchestrator:
1. Validates syntax, checks import blocklist, verifies no top-level side effects.
2. Deploys the file here as `problem/helpers/<name>.py`.
3. Updates this README and the orchestrator's `_helpers_section()` prompt.

Do **not** add files directly to this directory — always go through the experimentator workflow.
