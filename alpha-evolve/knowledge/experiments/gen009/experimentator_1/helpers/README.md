# Problem Helpers Index

All helper modules live in `problem/helpers/`. Import in solution files as:
```python
from helpers.<module> import <function>
```
(`evaluate.py` adds `problem/` to `sys.path` so `helpers/` is directly importable.)

---

## Built-in Helpers

### `core.py` — JAX differentiable C computation

**Function:** `compute_c(f_values: jnp.ndarray) -> float`

Computes the autocorrelation constant C = max(f★f)*dx / (∫f)² using JAX float32.
Supports `jax.grad()` for gradient-based optimization.

**Use for:** gradient computation, JAX-based optimization (L-BFGS, Adam, etc.)
**Do NOT use for:** accept/reject decisions (float32 precision ~1e-6 is insufficient)

```python
from helpers.core import compute_c
import jax
grad_fn = jax.grad(compute_c)
```

---

### `compute_c_f64.py` — Float64 C computation matching validate.py

**Function:** `compute_c_f64(f_array) -> float`

Computes C using numpy float64 throughout. Matches `validate.py` exactly (~1e-15 precision).

**Use for:** all accept/reject decisions, verification, benchmark comparisons

```python
from helpers.compute_c_f64 import compute_c_f64
c = compute_c_f64(f_array)  # float64, matches evaluate.py output
```

---

## Experimentator-Created Helpers

### `cross_convolution_f64.py` — Float64 autoconvolution and tight-constraint helpers

**Functions:**

`autoconvolve(f, dx=None) -> (autoconv, f_padded, dx, M_fft)`
- Computes (f★f) in float64, returns full length-2N array (same convention as incremental_update)
- Returns f_padded (zero-padded f) needed for incremental updates
- Clamps negative values to 0 (matching validate.py)

`cross_convolve(f, g, dx=None) -> conv`
- Linear convolution of two different arrays, length 2N-1

`tight_constraint_indices(f, epsilon_rel=1e-5) -> indices`
- Returns indices where autoconv ≥ max*(1-epsilon_rel)
- Use epsilon_rel=1e-6 for 1-3 tight constraints; 1e-5 for ~5-20 constraints

```python
from helpers.cross_convolution_f64 import autoconvolve, tight_constraint_indices
autoconv, f_padded, dx, M = autoconvolve(f)
tight_idx = tight_constraint_indices(f, epsilon_rel=1e-5)
```

---

### `incremental_autoconv_update.py` — O(N) incremental autoconvolution update

**Functions:**

`incremental_update(autoconv, f_padded, idx, delta, dx, M_fft) -> new_autoconv`
- Updates autoconvolution when `f[idx] += delta` without recomputing FFT
- ~28x faster than FFT recompute at N=30000
- **Does NOT modify arrays in-place.** Caller must do `f_padded[idx] += delta` separately.
- Exact to floating-point precision (bit-identical to FFT recompute)

`batch_incremental_updates(autoconv, f_padded, indices, deltas, dx, M_fft) -> (autoconv, f_padded)`
- Applies multiple updates sequentially
- **Modifies both arrays in-place**

```python
from helpers.incremental_autoconv_update import incremental_update
new_ac = incremental_update(autoconv, f_padded, idx, delta, dx, M)
f_padded[idx] += delta  # caller updates f_padded manually
```

---

### `batch_trial_evaluator.py` — Vectorized K-candidate batch predictor

**Function:** `batch_predict_c(autoconv, f_padded, dx, M_fft, indices_batch, deltas_batch, window_half=300, epsilon_rel=1e-5) -> (K,) array`

Evaluates K candidate moves simultaneously using first-order prediction, enabling
~50x speedup over sequential `incremental_update` calls.

**Performance at K=100, N=30000:** ~10-25ms vs ~680ms sequential (~50x speedup)
**Accuracy:** machine precision (<1e-14 relative error) for |delta| < 1e-3

Args:
- `indices_batch`: (K, k) int array — k indices per candidate (triplet: k=3, quadruplet: k=4, etc.)
- `deltas_batch`: (K, k) float64 — deltas summing to ≈0 per row for integral-preserving moves

**Typical usage (filtering workflow):**
```python
from helpers.batch_trial_evaluator import batch_predict_c
from helpers.cross_convolution_f64 import autoconvolve

autoconv, f_padded, dx, M = autoconvolve(f)

# Generate K=1000 candidates, predict all in <100ms
K, k = 1000, 4
indices = rng.integers(0, N, (K, k))
deltas = rng.standard_normal((K, k)) * 1e-5
deltas -= deltas.mean(axis=1, keepdims=True)  # integral-preserving

predicted_c = batch_predict_c(autoconv, f_padded, dx, M, indices, deltas)

# Keep top 5%: verify with exact evaluation
top_k = np.argsort(predicted_c)[:K//20]
for j in top_k:
    new_ac = incremental_update(autoconv, f_padded, ...)
    # accept/reject based on exact C
```

**Limitation:** Window covers ±300 positions around the current max. For |delta| > 0.01,
the true max may shift outside the window — underestimates C. Use as pre-filter only.

---

### `lp_matrix.py` — Vectorized LP constraint matrix for autocorrelation refinement

**Functions:**

`build_lp_matrix(f, tight_indices, dx=None) -> (A_ub, M_fft, f_padded)`
- Builds linearized LP constraint matrix A_ub[j, k] = 2 * f_padded[(j-k)%M] * dx
- Shape: (n_tight, N). At N=30000, n_tight=100: ~24MB. Vectorized, no Python loops.

`build_lp_rhs(autoconv, tight_indices, epsilon=0.0) -> (b_ub, A_max)`
- Builds right-hand side b_ub[j] = A_max - autoconv[tight_idx[j]] - epsilon

`scipy_lp_solve(f, tight_indices, autoconv, dx=None, epsilon=1e-9, max_step=0.1, integral_tol=1e-10) -> result dict`
- Solves the full LP: minimize slack t s.t. A_ub@delta ≤ b_ub+t, sum(delta)=0, f+delta≥0
- Returns dict with keys: `delta`, `predicted_improvement`, `status`, `message`
- **Note:** `predicted_improvement` is negative when improvement found (sign convention)
- **Note:** The LP constraint `t ≥ 0` means t=0 is the best possible outcome (no worsening).
  Always do a line search on the returned delta even if `predicted_improvement=0`.

```python
from helpers.lp_matrix import scipy_lp_solve
from helpers.cross_convolution_f64 import tight_constraint_indices, autoconvolve
autoconv, f_padded, dx, M = autoconvolve(f)
tight = tight_constraint_indices(f, epsilon_rel=1e-6)
result = scipy_lp_solve(f, tight, autoconv, epsilon=1e-9)
if result['status'] == 0:
    delta = result['delta']
    # apply delta via incremental_update
```

---

### `interpolation.py` — Structure-preserving interpolation

**Function:** `interpolate_sparse(array, target_n, threshold=1e-4) -> array`

Upsample/downsample while preserving near-zero structure as exact zeros.
Uses piecewise-linear interpolation for non-zero regions.

```python
from helpers.interpolation import interpolate_sparse
f_highres = interpolate_sparse(f_lowres, target_n=30000)
```

---

### `inv_softplus.py` — Safe inverse softplus for warm-start

**Function:** `inv_softplus_safe(f, eps=1e-8, clip_min=-10.0, clip_max=30.0) -> raw_params`

Converts non-negative f values to raw parameters for softplus parameterization:
`softplus(inv_softplus_safe(f)) ≈ f`. Handles near-zero elements safely.

```python
from helpers.inv_softplus import inv_softplus_safe
raw = inv_softplus_safe(f)
# Then optimize raw_params with JAX, recover f = jax.nn.softplus(raw_params)
```

---

### `sensitivity.py` — Gradient / sensitivity analysis

**Function:** `sensitivity_map(f_array, use_float64=False) -> gradients`

Computes dC/df[i] for all elements.
- `use_float64=False`: JAX float32 autodiff (fast, ~1e-6 precision)
- `use_float64=True`: numpy float64 finite differences (slow, ~1e-8 precision, needed for C < 1.505)

```python
from helpers.sensitivity import sensitivity_map
grads = sensitivity_map(f, use_float64=True)  # float64 for micro-optimization
# Elements with large positive grads are candidates for reduction
worst_idx = np.argsort(grads)[-10:]  # top-10 elements that raise C most
```

---

## Helper deployment notes

- `coordinate_descent.py` was prototyped in gen008 but NOT deployed (validation incomplete).
  Do not import it; it is not present in `problem/helpers/`.
- `problem/helper.py` is a backward-compatibility shim that re-exports `compute_c` from
  `helpers/core.py`. Old solutions using `from helper import compute_c` still work, but
  new solutions should use `from helpers.core import compute_c`.
