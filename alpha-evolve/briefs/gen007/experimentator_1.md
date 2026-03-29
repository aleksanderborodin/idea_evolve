# experimentator_1 — Generation 7

## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen006/exploit_1/sol01.py` → C = 1.5028628724712894
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank02_1.502863.py` → C = 1.502862898

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md` — Current helper index (STALE — says "none yet" but 4 helpers exist)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — Existing float64 C helper (reference for style)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/core.py` — Built-in JAX helper (reference)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/sensitivity.py` — Existing sensitivity helper
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen006/exploit_1.md` — Contains incremental autoconv formula
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen006/full_1.md` — Contains LP bottleneck analysis
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md` — Problem definition (autoconvolution structure)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md` — Autoconvolution details

## Directive

**Mission: Create 3 shared helper tools + update README.**

These helpers directly unblock the two highest-value experiments (coordinate descent and LP) for future generations. In gen 6, exploit_1 spent 30+ minutes deriving the incremental autoconv update from scratch — this must not happen again.

### Helper 1: `incremental_autoconv_update.py`

**Question:** Can we package the O(N) incremental autoconvolution update as a reusable helper?

**Implementation:**
```python
def incremental_update(autoconv, f_padded, idx, delta, dx, M_fft):
    """
    Update autoconvolution in-place when f[idx] changes by delta.
    O(N) instead of O(N log N) FFT recomputation.

    Args:
        autoconv: current autoconvolution array (length M = 2N-1, zero-padded to M_fft)
        f_padded: zero-padded f array (length M_fft)
        idx: index of changed element
        delta: change amount (f[idx] += delta)
        dx: grid spacing (0.5 / N)
        M_fft: FFT padding size

    Returns:
        Updated autoconv array, updated max value
    """
    # autoconv[n] += 2 * delta * f_padded[(n - idx) % M_fft] * dx
    # autoconv[2*idx] += delta^2 * dx  (self-convolution term)
    ...
```

**Validation:** Compare against full FFT recomputation on 5 random perturbations. Max difference should be < 1e-14.

### Helper 2: `cross_convolution_f64.py`

**Question:** Can we provide a clean float64 cross-convolution helper for LP constraint matrix construction?

**Implementation:**
```python
def cross_convolve(f, g, dx=None):
    """
    Compute (f ★ g)(t) via FFT in float64.

    Args:
        f, g: 1D numpy arrays (same length N)
        dx: grid spacing (default: 0.5 / N)

    Returns:
        Cross-convolution array of length 2N-1
    """
    ...

def tight_constraint_indices(f, epsilon_rel=1e-5):
    """
    Find indices where autoconvolution is within epsilon of its maximum.

    Args:
        f: 1D numpy array
        epsilon_rel: relative tolerance (fraction of max_autoconv)

    Returns:
        Array of tight constraint indices
    """
    ...
```

### Helper 3: `lp_matrix.py`

**Question:** Can we package the LP constraint matrix builder using vectorized FFT?

**Implementation:**
```python
def build_lp_matrix(f, tight_indices, dx=None):
    """
    Build the linearized LP constraint matrix A_ub for autocorrelation refinement.
    A_ub[j, k] = 2 * f_padded[(j - k) % M_fft] * dx

    Vectorized construction — NO Python loops over N.

    Args:
        f: 1D numpy array (length N)
        tight_indices: indices where autoconv is near max
        dx: grid spacing (default: 0.5 / N)

    Returns:
        A_ub: (n_tight, N) constraint matrix
    """
    ...
```

### Task 4: Update README.md

Update `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md` to document ALL existing helpers:
- `core.py` (compute_c, JAX float32)
- `compute_c_f64.py` (compute_c_f64, numpy float64)
- `sensitivity.py` (sensitivity_map, supports float64 mode)
- `inv_softplus.py` (inv_softplus_safe — NOTE: use clip_min=-20 for sparse arrays)
- `interpolation.py` (description based on reading the file)
- Plus the 3 new helpers above

### Methodology
1. Read existing helpers for style and conventions
2. Implement each helper with proper docstrings and input validation
3. Write unit tests for each helper (test against full FFT recomputation)
4. Write all helpers to `output/helpers/`
5. Write updated README to `output/helpers/README.md`
6. Write `output/report.md` with test results

### Success criteria
- All 3 helpers pass validation tests
- incremental_update matches full FFT to < 1e-14 on 5 test cases
- cross_convolve matches numpy reference implementation
- build_lp_matrix produces correct Toeplitz structure
- README is complete and accurate
