# full_1 — Generation 7

## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen006/exploit_1/sol01.py` → C = 1.5028628724712894
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank02_1.502863.py` → C = 1.502862898

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md` — Strategic overview
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_003.md` — Published solutions cluster (LP context)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_020.md` — LP-based refinement (failed in gen 6, math is sound)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_011.md` — LP constraint matrix construction bottleneck
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen006/full_1.md` — Gen 6 LP attempt debrief (OOM at N=30k, has root cause analysis)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen006/exploit_1/sol01.py` — Best solution (N=30000, C=1.5028628724712894)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — Float64 C computation

## Directive

**Mission: LP-based refinement proof-of-concept at reduced resolution N=2000.**

Gen 6 full_1 implemented the correct LP formulation but failed because constraint matrix construction at N=30000 consumed 7GB RAM. The fix: work at N=2000 first, then upsample the descent direction.

### CRITICAL IMPLEMENTATION GUIDANCE — DO NOT USE PYTHON LOOPS FOR MATRIX CONSTRUCTION

The gen 6 failure was caused by building `A_ub[j, k]` in a nested Python loop. Use batched FFT instead:

```python
import numpy as np
from scipy.optimize import linprog

# Step 1: Downsample best solution from N=30000 to N=2000
f_30k = load_best_solution()  # from population/gen006/exploit_1/sol01.py
N_lp = 2000
x_orig = np.linspace(-0.25, 0.25, len(f_30k), endpoint=False)
x_new = np.linspace(-0.25, 0.25, N_lp, endpoint=False)
f = np.interp(x_new, x_orig, f_30k)
f = np.maximum(f, 0)  # ensure non-negativity after interpolation

dx = 0.5 / N_lp

# Step 2: Compute autoconvolution via FFT
M = 2 * N_lp - 1
M_fft = int(2 ** np.ceil(np.log2(M)))
F = np.fft.rfft(f, n=M_fft)
autoconv = np.fft.irfft(F * F, n=M_fft)[:M] * dx
max_autoconv = np.max(autoconv)

# Step 3: Find tight constraints (indices where autoconv is near max)
# Start with epsilon = 1e-5 * max_autoconv for minimal LP
epsilon = 1e-5 * max_autoconv
tight_indices = np.where(autoconv >= max_autoconv - epsilon)[0]
print(f"Tight constraints: {len(tight_indices)} at epsilon={epsilon:.2e}")

# If too many (>200), increase epsilon. If zero, decrease.
# Target: 5-50 tight constraints for proof-of-concept.

# Step 4: Build constraint matrix using VECTORIZED FFT
# For linearized objective: delta_autoconv[j] ≈ 2 * (f ★ delta_f)[j] * dx
# A_ub[j, k] = 2 * f[j - k] * dx  (convolution structure)
# This is a Toeplitz matrix! Build it efficiently:

# Method: Each row j of A_ub is f reversed and shifted
# A_ub[j, k] = 2 * f_padded[j - k] * dx
f_padded = np.zeros(M_fft)
f_padded[:N_lp] = f

# Build A_ub using circular indexing (vectorized):
n_tight = len(tight_indices)
A_ub = np.zeros((n_tight, N_lp))
for j_idx, j in enumerate(tight_indices):
    # Row j: A_ub[j, k] = 2 * f_padded[(j - k) % M_fft] * dx for k in [0, N_lp)
    indices = (j - np.arange(N_lp)) % M_fft
    A_ub[j_idx, :] = 2 * f_padded[indices] * dx
# This is ONE loop over tight constraints (5-50), not N_lp. Fast.

# Step 5: Formulate LP
# Minimize: max over tight j of (autoconv[j] + A_ub[j, :] @ delta_f)
# Subject to: f + delta_f >= 0  =>  delta_f >= -f
# Integral preservation: sum(delta_f) = 0
# Introduce auxiliary variable t: A_ub @ delta_f <= t (for all j)
# Minimize t

# Variables: [delta_f (N_lp), t (1)]
c_obj = np.zeros(N_lp + 1)
c_obj[-1] = 1.0  # minimize t

# Constraints: A_ub @ delta_f - t <= -residual[j] (to push max down)
residual = autoconv[tight_indices] - max_autoconv  # all <= 0
A_ineq = np.hstack([A_ub, -np.ones((n_tight, 1))])
b_ineq = -residual  # push autoconv at tight points down

# Bounds: delta_f >= -f, t unbounded
bounds = [(-f[k], None) for k in range(N_lp)] + [(None, None)]

# Equality: sum(delta_f) = 0
A_eq = np.zeros((1, N_lp + 1))
A_eq[0, :N_lp] = 1.0
b_eq = np.array([0.0])

result = linprog(c_obj, A_ub=A_ineq, b_ub=b_ineq, A_eq=A_eq, b_eq=b_eq,
                 bounds=bounds, method='highs')

# Step 6: Extract and apply descent direction
if result.success and result.x[-1] < 0:  # t < 0 means we found improvement direction
    delta_f_lp = result.x[:N_lp]

    # Upsample delta_f to N=30000
    delta_f_30k = np.interp(x_orig, x_new, delta_f_lp)

    # Line search: try step sizes
    for alpha in [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]:
        f_new = f_30k + alpha * delta_f_30k
        f_new = np.maximum(f_new, 0)  # project to non-negative
        c_new = compute_c_f64(f_new)
        print(f"alpha={alpha}: C={c_new}")
```

### Validation requirements
- If constraint matrix construction takes > 60 seconds at N=2000, STOP and reduce to N=1000.
- After LP solve: verify the descent direction actually reduces C on the downsampled array before upsampling.
- Use `compute_c_f64` for all C evaluations.

### If LP succeeds at N=2000
- Try N=3000, N=5000 to see how LP quality scales with resolution.
- Try multiple epsilon values to vary the number of tight constraints.
- Report the LP objective value, number of active constraints, and descent magnitude.

### If LP direction fails after upsampling
- This means the LP structure is resolution-sensitive.
- Try applying the LP direction at N=2000 directly (without upsampling) and report the N=2000 result.

### What NOT to do
- Do NOT build constraint matrix in a Python loop over N (that's what killed gen 6)
- Do NOT attempt full resolution N=30000 LP (even with batched FFT, start small)
- Do NOT use smooth-max Adam

### Success criteria
- Primary: LP produces a descent direction that improves C (at any resolution)
- Secondary: Successful LP solve at N=2000 in < 60 seconds
- Tertiary: Upsampled LP direction improves the N=30000 array
