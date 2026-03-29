## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` → C = 1.5028628894 (TTT-Discover 30k + coord descent)
Gradient-descent best: C = 1.5090 (`/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen003/explore_2/sol01.py`)
N=600 warm-start targets: C=1.5040 (`/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen005/research_1/sol02.py`), C=1.5053 (`/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen005/research_1/sol01.py`)
Target: C ≤ 1.5053 — **BEATEN**

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen005/research_1/sol02.py` — N=600 AlphaEvolve array, C=1.5040 (primary warm-start target)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen005/research_1/sol01.py` — N=600 AlphaEvolve array, C=1.5053 (secondary target)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_007.md` — Published solutions are local minima for smooth-max Adam (tested float32 only)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_008.md` — Float32/float64 precision mismatch
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_002.md` — Problem representation cluster (stale, but N=600 arrays may revive it)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/core.py` — JAX float32 compute_c (for gradients)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/inv_softplus.py` — inv_softplus_safe for conversion
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/validate.py` — Float64 ground truth
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md` — Problem definition
- `/home/sasha/Desktop/project_alpha/alpha-evolve/history/coverage_matrix.md` — What's been tried

## Directive

**Warm-start smooth-max Adam from N=600 LP-optimized arrays using float64 accept/reject decisions. These arrays are directly pipeline-compatible — no interpolation needed.**

The N=600 arrays from AlphaEvolve (C=1.5040, C=1.5053) are LP-optimized at the SAME resolution as our gradient pipeline. They represent a genuinely different structural family from random-init gradient solutions. Pattern_007 (warm-start failure) was only tested on the 1319-element array at float32 precision. These N=600 arrays have never been warm-started.

### Protocol

1. **Implement float64 compute_c** in numpy (copy from validate.py):
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

2. **Warm-start from sol02 (C=1.5040, N=600):**
   - Load array from `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen005/research_1/sol02.py`
   - Convert to raw_params via inv_softplus_safe
   - Run smooth-max Adam with temperature annealing:
     - T = [0.05, 0.01, 0.003, 0.001, 0.0003]
     - 15,000 steps per phase
     - Adam lr=1e-3
     - 4 seeds with diverse perturbations (sigma=0.01 * std(raw_params))
   - **Use float64 compute_c for tracking C after each phase** (JAX float32 for gradient computation is fine)
   - Track: starting C, C after each phase, final C

3. **Compare to baseline:** Does the optimizer improve below C=1.5040, or does it converge to the ~1.509 gradient attractor?
   - If C < 1.5040: SUCCESS — warm-start works at N=600, Pattern_007 is resolution-dependent
   - If C ≈ 1.509: The gradient attractor dominates regardless of warm-start quality

4. **Also try sol01 (C=1.5053)** with the same protocol. Different starting C, different structure.

5. **If warm-start fails, try float64 coordinate descent on sol02:**
   - Same technique as gen 5 exploit_2 (idea_019)
   - Top-500 elements by sensitivity, deltas [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
   - 10 passes with gradient recomputation
   - These N=600 arrays may have more room for coordinate descent than the 30k array

### Off-limits (do NOT attempt)
- SA at any coarse scale (pattern_009 — confirmed dead end)
- L-BFGS (idea_010 — debunked)
- DCT perturbation (idea_015 — debunked)
- Gaussian mixture parameterization (C=1.5418, failed gen 5)
- Random perturbation search (failed gen 5)

### MANDATORY: Bake your best result
Final solution must contain the optimized array as a literal numpy array in `entrypoint()`. No optimization at eval time.
