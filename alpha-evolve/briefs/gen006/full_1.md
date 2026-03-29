## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` → C = 1.5028628894 (TTT-Discover 30k + coord descent)
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank02_1.5029.py` → C = 1.5029 (TTT-Discover 30k verbatim)
Target: C ≤ 1.5053 — **BEATEN**

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_020.md` — LP-based refinement concept
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_018.md` — TTT-Discover method (LP with heuristic focusing)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_003.md` — Published solutions cluster (frontier is here)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank02_1.5029.py` — TTT-Discover 30k verbatim array (use this, NOT best.py which takes 792s)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen005/exploit_1.md` — Why all gradient methods fail on this array
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/validate.py` — Ground truth evaluator (float64, shows FFT autoconvolution computation)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md` — Problem definition
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md` — Constraints

## Directive

**Implement LP-based constraint relaxation to refine the TTT-Discover 30k array. This is the only optimization method that has ever produced sub-1.505 scores — and it has NEVER been attempted in our pipeline.**

Both AlphaEvolve (C=1.5032) and TTT-Discover (C=1.5029) were produced by LP-based methods. Five agent reports across two generations identified LP as the only viable path forward after gradient methods exhaustively failed. This is the highest-priority experiment in the system.

### Background

The autocorrelation constant is: C(f) = max_{t} (f★f)(t) / (∫f)²

Near the optimum, the autoconvolution (f★f)(t) approaches C·(∫f)² at many positions t — these are "near-tight constraints." An LP can find a direction to move f that simultaneously relaxes these tight constraints while maintaining feasibility (f ≥ 0, integral preserved).

### Implementation plan

1. **Float64 compute_c.** Implement in numpy float64 matching validate.py (NOT JAX float32):
   ```python
   def compute_c_f64(f):
       N = len(f)
       dx = 0.5 / N
       n_padded = 1
       while n_padded < 2 * N - 1:
           n_padded *= 2
       F = np.fft.rfft(f, n=n_padded)
       autoconv = np.fft.irfft(F * F, n=n_padded)[:2*N-1] * dx
       integral = np.sum(f) * dx
       return float(np.max(autoconv) / (integral ** 2))
   ```

2. **Autoconvolution analysis.** For the TTT-Discover array:
   - Compute full autoconvolution: `autoconv = irfft(rfft(f)**2) * dx`
   - Find max value and its index (the "peak")
   - Find all indices where `autoconv[i] > max * (1 - epsilon)` for epsilon in [0.001, 0.01, 0.1]
   - These are the near-tight constraints. Report how many there are at each threshold.

3. **LP formulation (simplified).** Use `scipy.optimize.linprog`:
   - Decision variable: δ (perturbation vector, length N)
   - Objective: minimize max autoconvolution after perturbation (or equivalently, minimize C)
   - Constraints:
     - `f[i] + δ[i] ≥ 0` for all i (non-negativity)
     - `sum(δ) = 0` (preserve integral, or relax to `sum(δ) ≥ 0`)
     - For each near-tight index j: `(f+δ) ★ (f+δ)[j] ≤ target_max`
   - The autoconvolution constraint is quadratic in δ, so linearize around current f:
     - `(f+δ)★(f+δ) ≈ f★f + 2·(f★δ)` (first-order approximation)
     - The constraint becomes: `f★f[j] + 2·(f★δ)[j] ≤ target_max` for tight indices j
   - Use the linearized LP to find a descent direction δ

4. **Apply LP step.** After solving the LP:
   - Apply `f_new = f + alpha * δ` for step sizes alpha in [0.001, 0.01, 0.1, 0.5, 1.0]
   - Project: `f_new = max(f_new, 0)`
   - Compute C(f_new) with float64
   - Accept the best alpha

5. **Iterate.** Repeat steps 2-4 multiple times (target: 10-50 LP iterations). The near-tight constraints change after each step, so recompute them.

6. **Fallback: simplified LP.** If the full LP is too slow at N=30000:
   - Reduce to top-K most sensitive elements only (K=500-2000)
   - Or work on a downsampled version and upsample the direction
   - Or focus on the K nearest-to-peak autoconvolution indices

### Engineering notes
- `scipy.optimize.linprog` uses the HiGHS solver (fast for large sparse LPs)
- The linearized convolution constraint `2·(f★δ)[j]` can be computed via FFT (fast)
- For N=30000, the LP has 30000 variables and K constraints (K = number of near-tight indices)
- If K is small (< 100), this is a very tractable LP
- If K is large (> 1000), consider iterating: solve LP for top-100 tightest, apply, repeat

### What NOT to do
- Do NOT use gradient descent (Adam, L-BFGS, projected gradient) — all failed (gen 5)
- Do NOT use smooth-max approximation — the smooth-max error is larger than the improvements we seek
- Do NOT modify the array at random — random perturbation search failed (gen 5)

### MANDATORY: Bake the final array
Your solution must contain the optimized array as a literal numpy array in `entrypoint()`. No optimization at eval time. Target eval time < 5 seconds.

### Success criteria
- C < 1.5028628894 (any improvement over current best)
- If LP finds no descent direction: report WHY (how many constraints are tight, what the LP status is) — this is valuable information even as a negative result
