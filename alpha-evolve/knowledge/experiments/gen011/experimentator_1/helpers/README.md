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

### `batch_trial_evaluator.py` — Vectorized batch trial evaluator

| Function | Signature | Description |
|----------|-----------|-------------|
| `batch_evaluate_trials` | `(f, autoconv, f_padded, dx, M, trials, ...)` | Vectorized batch trial evaluator for k-element integral-preserving moves. |

Import: `from helpers.batch_trial_evaluator import batch_evaluate_trials`

### `compute_c_f64.py` — Float64 compute_c

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_c_f64` | `(f_array) -> float` | Float64 C computation matching validate.py exactly. Use for all accept/reject decisions. |

Import: `from helpers.compute_c_f64 import compute_c_f64`

### `cross_convolution_f64.py` — Cross-convolution helpers

Float64 cross-convolution and tight-constraint helpers for LP refinement.

Import: `from helpers.cross_convolution_f64 import <function>`

### `incremental_autoconv_update.py` — O(N) incremental autoconvolution update

| Function | Signature | Description |
|----------|-----------|-------------|
| `incremental_update` | `(autoconv, f_padded, idx, delta, dx, M_fft) -> new_autoconv` | O(N) update when f[idx] changes by delta. ~28x faster than FFT recomputation. |
| `batch_incremental_updates` | `(autoconv, f_padded, indices, deltas, dx, M_fft) -> (autoconv, f_padded)` | Apply multiple incremental updates sequentially. Modifies in-place. |

Import: `from helpers.incremental_autoconv_update import incremental_update`

### `interpolation.py` — Structure-preserving interpolation

| Function | Signature | Description |
|----------|-----------|-------------|
| (various) | | Structure-preserving interpolation for sparse solution arrays. |

Import: `from helpers.interpolation import <function>`

### `inv_softplus.py` — Safe inverse softplus

| Function | Signature | Description |
|----------|-----------|-------------|
| `inv_softplus` | `(x) -> array` | Safe inverse softplus for warm-start optimization. |

Import: `from helpers.inv_softplus import inv_softplus`

### `lp_matrix.py` — LP constraint matrix builder

| Function | Signature | Description |
|----------|-----------|-------------|
| (various) | | Vectorized LP constraint matrix builder for autocorrelation refinement. |

Import: `from helpers.lp_matrix import <function>`

### `plateau_analyzer.py` — Autoconvolution plateau analyzer

| Function | Signature | Description |
|----------|-----------|-------------|
| `plateau_analysis` | `(f, autoconv=None, threshold_rel=1e-12) -> dict` | Finds near-max autoconv positions + per-element gradients. For minimax strategies. |

Import: `from helpers.plateau_analyzer import plateau_analysis`

### `sensitivity.py` — Sensitivity analysis

| Function | Signature | Description |
|----------|-----------|-------------|
| (various) | | Sensitivity analysis for autocorrelation solutions. |

Import: `from helpers.sensitivity import <function>`

### `topk_screened_cd.py` — Coordinate descent with top-K screening and FFT resync *(NEW — gen 11)*

| Function | Signature | Description |
|----------|-----------|-------------|
| `topk_screened_cd` | `(f, K=30, deltas=None, resync_interval=1, max_rounds=200, deadline=None, verbose=False) -> dict` | Complete CD optimizer combining top-K screening (~50x speedup), periodic FFT resync (drift elimination), and geometric delta grid. Returns dict with optimized `f`, verified `C`, improvement count, and per-round log. |

Import: `from helpers.topk_screened_cd import topk_screened_cd`

**Usage example:**
```python
import numpy as np
from helpers.topk_screened_cd import topk_screened_cd
import time

f = ...  # your starting array
result = topk_screened_cd(f, K=30, max_rounds=100, deadline=time.time() + 300)
f_optimized = result['f']  # numpy float64 array
C_final = result['C']      # verified C value
```

---

## How helpers are added

Experimentator agents write helpers to `output/helpers/<name>.py`. The orchestrator:
1. Validates syntax, checks import blocklist, verifies no top-level side effects.
2. Deploys the file here as `problem/helpers/<name>.py`.
3. Updates this README and the orchestrator's `_helpers_section()` prompt.

Do **not** add files directly to this directory — always go through the experimentator workflow.
