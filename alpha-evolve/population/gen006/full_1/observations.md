# gen006_full_1 Observations

## Approach: LP-based constraint relaxation on TTT-Discover 30k array

### What was attempted

Implemented a linearized LP approach to refine the TTT-Discover 30k array (C=1.502862898255827):

1. **Autoconvolution analysis** — Computed full autoconvolution via FFT in float64. Identified near-tight constraints at various epsilon thresholds.

2. **Linearized LP formulation** — For each near-tight constraint index j:
   - `(f+δ)★(f+δ) ≈ f★f + 2·(f★δ)` (first-order Taylor expansion)
   - LP minimizes max over tight constraints of `f★f[j] + 2·(f★δ)[j]`
   - Subject to: `f[i] + δ[i] >= 0`, `sum(δ) = 0` (preserve integral), `|δ[i]| <= 0.005`

3. **Implementation** — Used scipy.optimize.linprog with HiGHS solver and sparse constraint matrices.

### What happened

The LP construction phase consumed excessive memory (~7GB) and time (>19 minutes) before being killed. The root cause: building the sparse constraint matrix requires iterating over (n_active × n_tight) pairs where n_active can be ~2000 and n_tight can be ~1000+. At N=30000, even the FFT-based cross-convolution for each active variable is expensive when done in a Python loop.

### Key bottleneck

The constraint matrix `A_ub[j, k] = 2 * f[j - active[k]] * dx` can in principle be computed via vectorized indexing, but the Python loop over (tight_idx, active_idx) pairs was too slow. A proper implementation would:
1. Precompute the entire cross-convolution `f★e_k` for all active k using batched FFT
2. Extract the tight-index rows from each cross-convolution
3. Stack into the constraint matrix

This is feasible but requires careful memory management (2000 FFTs of length 60000).

### Result

No improvement achieved. Sol01 is the unmodified TTT-Discover array (C=1.502862898255827).

### Insights for future agents

1. **LP at N=30k is tractable but needs vectorized construction.** The LP itself (2000 variables, ~100 tight constraints) would solve in seconds via HiGHS. The bottleneck is constructing the constraint matrix.

2. **Better approach: work at reduced resolution.** Downsample the 30k array to N=1000-3000, run LP there, then upsample the delta direction and apply to the full array. The LP descent direction doesn't need full-resolution fidelity.

3. **Alternative: column generation.** Instead of pre-computing all 2000 columns of the constraint matrix, use column generation — start with a few variables, solve the LP, check reduced costs to add new variables. This avoids computing all cross-convolutions.

4. **The number of truly tight constraints is small.** At epsilon=0.0001, there may be only 1-5 tight constraints. The LP would then be tiny (2000 vars, 5 constraints). The issue is just the matrix construction.
