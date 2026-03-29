# Problem Helpers

All reusable helpers live here. Import them in solution files as:

    from helpers.<module> import <function>

`evaluate.py` adds `problem/` to `sys.path`, so `helpers/` is directly importable.

---

## Built-in helpers

### `core.py` — Problem-specific core helper (JAX float32)

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_c` | `(f_values: jnp.ndarray) -> float` | JAX-based, differentiable. Computes C = max(f*f) / (integral f)^2 via FFT. **Precision: ~1e-6 (float32).** Use for gradient-based optimization and quick sanity checks. NOT suitable for accept/reject decisions on well-optimized solutions (C < 1.505). |

Import: `from helpers.core import compute_c`

---

## Experimentator-created helpers

### `compute_c_f64.py` — Float64 compute_c matching validate.py (numpy float64)

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_c_f64` | `(f_array) -> float` | Numpy float64 implementation of compute_c, **identical to validate.py's validate()**. **Precision: ~1e-15.** NOT differentiable (no JAX). Use for all accept/reject decisions in optimization. |

Import: `from helpers.compute_c_f64 import compute_c_f64`

**When to use which:**
- `compute_c` (float32): gradient computation, JAX autodiff, quick checks
- `compute_c_f64` (float64): accept/reject decisions, final scoring, coordinate descent

### `sensitivity.py` — Sensitivity analysis (float32 autodiff + float64 finite diff)

| Function | Signature | Description |
|----------|-----------|-------------|
| `sensitivity_map` | `(f_array, use_float64=False) -> array` | Computes dC/df[i] for all elements. Default: JAX float32 autodiff. With `use_float64=True`: numpy float64 central finite differences via `compute_c_f64`. Float64 mode is ~N times slower but essential for micro-optimization below C~1.505 (see pattern_008). |

Import: `from helpers.sensitivity import sensitivity_map`

### `inv_softplus.py` — Safe inverse softplus for warm-start optimization

| Function | Signature | Description |
|----------|-----------|-------------|
| `inv_softplus_safe` | `(f, eps=1e-8, clip_min=-10.0, clip_max=30.0) -> array` | Converts non-negative function values to raw parameters such that softplus(raw) approx f. Handles near-zero safely. Uses float64 internally. |

Import: `from helpers.inv_softplus import inv_softplus_safe`

### `interpolation.py` — Structure-preserving interpolation

| Function | Signature | Description |
|----------|-----------|-------------|
| `interpolate_sparse` | `(array, target_n, threshold=1e-4) -> array` | Upsample/downsample preserving near-zero regions as exact zeros. Piecewise-linear for non-zero regions. |

Import: `from helpers.interpolation import interpolate_sparse`

---

## How helpers are added

Experimentator agents write helpers to `output/helpers/<name>.py`. The orchestrator:
1. Validates syntax, checks import blocklist, verifies no top-level side effects.
2. Deploys the file here as `problem/helpers/<name>.py`.
3. Updates this README and the orchestrator's `_helpers_section()` prompt.

Do **not** add files directly to this directory — always go through the experimentator workflow.
