## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` → C = 1.5028628894 (TTT-Discover 30k, float64 coord descent)
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank02_1.5029.py` → C = 1.5029 (TTT-Discover 30k verbatim)
Third best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank03_1.5029.py` → C = 1.5029
Target: C ≤ 1.5053 — **BEATEN** (best is 0.0025 below target)

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_008.md` — Float32/float64 precision mismatch (the reason this helper is needed)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/core.py` — Current float32 JAX compute_c implementation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/sensitivity.py` — Current float32 sensitivity_map (needs float64 option)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md` — Helper index (needs updating)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/validate.py` — The float64 ground truth implementation to match
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/__init__.py` — Package init
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen005/exploit_2.md` — exploit_2's manual float64 reimplementation (reference)

## Directive

**Create `compute_c_f64` helper — this is the #1 requested helper across 3 consecutive generations.**

Both exploit agents in gen 5 spent 30+ minutes reimplementing float64 compute_c from scratch because the existing `helpers/core.py` uses JAX float32. This precision mismatch corrupts all optimization decisions for solutions below C~1.505 (pattern_008). Every future exploit agent will need float64. Build it once.

### Deliverables

1. **`output/helpers/compute_c_f64.py`** — Float64 version of compute_c matching validate.py exactly:
   ```python
   def compute_c_f64(f_array):
       """Float64 compute_c matching validate.py exactly.
       Uses numpy float64 throughout (no JAX). Precision: ~1e-15.
       Use for all accept/reject decisions in optimization.
       Use compute_c() (JAX float32) only for quick sanity checks or gradient computation.

       Args:
           f_array: 1D numpy array of non-negative function values on [-1/4, 1/4]
       Returns:
           float: C value in float64
       """
   ```
   Implementation: copy the FFT-based autoconvolution from validate.py's `validate()` function. Use `numpy.float64` throughout. Zero-pad to next power of 2. Return `max(autoconv * dx) / (sum(f) * dx)**2`.

2. **Update `output/helpers/sensitivity.py`** — Add a `use_float64=True` parameter:
   - When `use_float64=True`, compute sensitivity using `compute_c_f64` with finite differences
   - When `use_float64=False` (default), use existing JAX autodiff (backward compatible)
   - The float64 gradient computation should use central differences: `(C(f+delta) - C(f-delta)) / (2*delta)` with `delta=1e-8`

3. **Update `output/helpers/README.md`** — Complete index of ALL helpers with precision notes:
   - `core.py`: compute_c (JAX float32, differentiable, ~1e-6 precision)
   - `compute_c_f64.py`: compute_c_f64 (numpy float64, NOT differentiable, ~1e-15 precision)
   - `sensitivity.py`: sensitivity_map (supports both float32 JAX autodiff and float64 finite diff)
   - `inv_softplus.py`: inv_softplus_safe
   - `interpolation.py`: interpolate_solution

### Validation

After writing each helper:
1. Run `python3 evaluate.py ../population/best.py` to get the ground truth C value
2. Load best.py's array and compute C with your compute_c_f64 — must match to 10+ decimal places
3. Test sensitivity_map with `use_float64=True` — top-20 elements must differ from float32 (pattern_008 confirms this)
4. Write results to `output/report.md`

### Constraints
- No top-level side effects in helper files (no print, no file I/O at import time)
- No imports outside numpy, scipy, math, functools (no JAX in compute_c_f64)
- All helpers must be importable standalone
- Do NOT modify files in `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/` directly — write to `output/helpers/`
