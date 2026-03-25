# Observations — Explore 2, Generation 2
## SA Wrapper Around Smooth-Max Gradient Descent

### Summary of Results

| Solution | C (fitness) | Approach | Total steps |
|----------|-------------|----------|-------------|
| sol01    | 1.5176      | 2 seeds × 25k init + 40 SA iters × 3k inner (Adam) | 290k |
| sol02    | 1.5162      | 4 seeds × 75k init + 60 SA iters × 6k inner (Adam) | 660k |
| sol03    | 1.5108      | 8 seeds × 75k init + 60 SA iters × L-BFGS(300) | 600k + SA |
| gen001/sol03 | 1.5108  | 8 seeds × 75k Adam (no SA, existing baseline) | 600k |

### What SA Achieved

SA did NOT improve beyond the initial smooth-max Adam convergence in any variant tried. The best result (sol03, C=1.5108) exactly matches the existing gen001/sol03, meaning the SA phase added zero benefit.

### Root Cause Analysis

**Why SA failed to improve:**

1. **Insufficient inner optimization budget per SA step.**
   - sol01/sol02 used 3k–6k Adam inner steps. This is likely not enough to reach true convergence from a perturbed point. The perturbed function is far from the local minimum, and 6k steps may only get partway there — yielding an intermediate point that's worse than the original, not a new local minimum.
   - sol03 switched to L-BFGS (300 iterations), which should converge much faster. But L-BFGS with temp=0.001 still didn't escape.

2. **Wrong inner optimization temperature.**
   - The inner SA optimizer used cold temps (0.001–0.01). But after a large perturbation (sigma=0.25–0.35 × f_max), the function might need warmer temps (e.g., 0.05) to navigate the landscape before being refined with cold temps.
   - Starting L-BFGS cold from a heavily perturbed point may mean it converges back to the same local minimum it started from (or nearby).

3. **Perturbation scale may be wrong.**
   - With sigma=0.25–0.35 × f_max and N=600, the total L2 perturbation is ~sigma × f_max × sqrt(N) ≈ 0.3 × 5 × 24 ≈ 36. This is large — might be kicking the solution to a region that's worse than the starting basin, and the inner optimizer cannot recover.
   - OR: the perturbation is too small to escape the local basin, and the optimizer simply converges back to the same minimum.

4. **SA acceptance temperature calibration.**
   - T_anneal_0 = 0.004–0.008 should allow accepting solutions up to ~0.01 worse. Looking at the trajectory: after perturbation + re-optimization, most proposals likely come back near C=1.512–1.52. We accept worse solutions, but then re-perturb from those worse positions, potentially losing ground.
   - The SA never seems to visit C < 1.5108, suggesting we never found a path to the better basin.

### Key Insight: Local Minimum Stickiness

The C=1.5108 solution appears to be in a "sticky" local minimum. The smooth-max gradient descent consistently finds this same basin regardless of initialization (multiple seeds all converge nearby). The SA perturbations are not large enough to escape this basin, or when they do escape, the re-optimizer doesn't find the target basin at C≈1.503.

The Boyer et al. paper uses SA at the COARSE GRID stage (N=23 intervals), not at the fine grid (N=600). At N=23, there are far fewer local minima and each perturbation can actually explore meaningfully. At N=600, the landscape is extremely high-dimensional and perturbations in individual function values may not change the basin structure much.

### What Would Help

1. **Coarse-to-fine with SA at coarse stage**: Apply SA at N=30 (not N=600), then upsample. This was the Boyer et al. approach. The low-dimensional coarse landscape has fewer local minima.

2. **Much larger perturbations + much more inner steps**: sigma=1.0–2.0 with 50k inner Adam steps per SA iteration might actually escape. But this becomes computationally very expensive (50k × 60 = 3M steps).

3. **Different perturbation strategy**: Instead of random Gaussian noise, perturb in a structured way — e.g., add a localized bump at a specific location, or perturb the Fourier coefficients. This might explore more efficiently.

4. **Warm restart for inner optimizer**: After perturbation, start with warm smooth-max temperature (T=0.05) for the first few thousand inner steps before cooling. This would help navigate the landscape near the perturbed point.

### What Worked

The dynamic-temperature JIT trick worked correctly: passing temp as a JAX array (not Python float) to `smooth_compute_c_dyn` compiles the function once and handles all temperatures efficiently. This gave ~2-3x speedup over sol03's pattern of redefining @jax.jit closures per temperature.

### Hypotheses for Future Agents

- The target basin (C≈1.503) is likely "far away" in function space from the current best (C=1.5108).
- Coarse-to-fine is probably the right approach to find it (another agent is covering this).
- SA at fine resolution needs either (a) coarse-level guidance or (b) very large perturbations + very many inner steps to be effective.
- The L-BFGS inner optimizer is efficient for fine-tuning but not for basin-hopping — it has no mechanism to escape saddle points or local minima.
