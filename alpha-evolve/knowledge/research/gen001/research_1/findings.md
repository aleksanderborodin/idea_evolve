# Research Findings — First Autocorrelation Inequality: Mathematical Theory & Optimization

## Summary
The "first autocorrelation inequality" is the well-studied "supremum of autoconvolutions" problem
from additive combinatorics. The true infimum C* = inf_f max(f*f)/(∫f)² lies in [1.28, 1.5032].
The key actionable insight is that **gradient descent on 600-interval discretizations achieves
C ≤ 1.5032** (AlphaEvolve/ThetaEvolve), but requires better optimization than the baseline's
40,000 Adam steps. Coarse-to-fine and simulated annealing are the proven high-impact improvements.

---

## Finding 1: Problem Identity and Current State of the Art

**Relevance**: All agents — establishes the true target and what's achievable.

**Detail**:
This problem is known in the mathematics literature as the "supremum of autoconvolutions"
inequality, studied in the context of **Sidon sets** in additive combinatorics. The constant is:

> C* = inf { max_{t ∈ [-1/2,1/2]} (f★f)(t) / (∫_{-1/4}^{1/4} f)² : f ≥ 0, f supported on [-1/4,1/4] }

**Current best known bounds (as of March 2026):**
- **Lower bound**: C* ≥ 1.28 (Cloninger & Steinerberger, 2017, arXiv:1403.7988)
- **Upper bound**: C* ≤ 1.50992 (Matolcsi & Vinuesa, 2010, arXiv:0907.1379) — explicit step function
- **Upper bound (improved)**: C* ≤ 1.5032 (AlphaEvolve, May 2025) — 600-interval gradient descent
- **Upper bound (matched)**: C* ≤ 1.503133 (ThetaEvolve, Nov 2025, arXiv:2511.23473)

**Our target of C ≤ 1.5053 is therefore ALREADY surpassed** in published literature. The actual
challenge is reaching 1.5032 or better.

The Schinzel-Schmidt conjecture that C* = π/2 ≈ 1.5708 was disproved by Matolcsi-Vinuesa.
The true minimum is unknown; there is no tight matching lower bound.

**Actionable implication**: Agents should target C ≤ 1.503, not just 1.5053. The gap between
1.28 (lower bound) and 1.5032 (best construction) means significant room remains for improvement.

---

## Finding 2: The Optimal Function is NOT Simple — Expect Complex Structure

**Relevance**: Explore and exploit agents — determines initialization and search strategy.

**Detail**:
The Matolcsi-Vinuesa paper (2010) **disproved** the Schinzel-Schmidt conjecture about the extremal
function's form. This means the optimal function is NOT a simple analytic function (not a constant,
not a cosine bell, not a Gaussian, not a tent function).

Evidence from the related L²-autoconvolution problem (2506.16750): the optimizer "consistently
discovers a comb-like motif in extremizing step functions, suggesting that optimal functions
have complex fine-scale structure."

The AlphaEvolve step function (600 intervals, C = 1.5032) and the Boyer et al. step function
(575 intervals) both show **non-symmetric, multi-peaked, irregular structure** — not
a smooth unimodal shape.

**What this means for specific initializations:**
- Starting from a **flat box function** (baseline) is suboptimal — gradient descent gets stuck
  at C ≈ 1.518-1.52, far from 1.503.
- Starting from a **Gaussian** or **cosine bell** similarly gives a bad local minimum.
- The best initialization is either:
  (a) A **coarse-grid optimized function** upsampled to fine grid (coarse-to-fine), or
  (b) The **converged function from a previous run** as warm start.

**Actionable implication**: Do NOT initialize from simple analytic functions expecting to
converge to the global optimum. Use coarse-to-fine or multi-restart strategies. The landscape
has many local minima.

---

## Finding 3: Coarse-to-Fine Optimization is the Most Effective Known Strategy

**Relevance**: Explore agents, exploit agents — the single highest-impact optimization change.

**Detail**:
The 2506.16750 paper (Boyer et al.) found their best function using this exact pipeline:
1. Start with N=23 intervals, run simulated annealing (~400 restarts) to find global minimum
2. Upsample to N=115 (5× per interval), run gradient ascent for ~1,000,000 steps
3. Upsample to N=575, run gradient refinement

Applied to our (minimization) problem:

```
Step 1: N=30, Adam optimizer, 20,000 steps, from uniform initialization
Step 2: Upsample to N=150 via jnp.interp, Adam, 20,000 steps
Step 3: Upsample to N=600, Adam, 30,000 steps + anneal
```

Upsampling in JAX:
```python
x_coarse = jnp.linspace(0, 1, N_coarse)
x_fine = jnp.linspace(0, 1, N_fine)
f_fine = jnp.interp(x_fine, x_coarse, f_coarse)
```

This is critical because: (1) the coarse grid quickly finds the right "basin" of the
global minimum without getting stuck in fine-scale local minima; (2) the fine grid
then refines within that basin.

**Expected result**: Coarse-to-fine should reach C ≈ 1.503-1.510 vs. the baseline's C ≈ 1.518.

**Actionable implication**: Replace the baseline single-scale Adam optimization with a
3-stage coarse-to-fine pipeline. Total compute time is similar (same total steps) but
convergence quality is much better.

---

## Finding 4: Simulated Annealing Escapes Local Minima That Gradient Descent Cannot

**Relevance**: Explore agents — key method for global optimization.

**Detail**:
The Boyer et al. paper explicitly used simulated annealing at the coarse stage to avoid
local minima, with a cooling schedule. For our problem, this means:

**Hybrid approach** (proven effective in the literature):
1. Run Adam to convergence (gets to local minimum)
2. Add random Gaussian noise: f ← f + σ * N(0,1), clip to ≥ 0
3. Run Adam again from the perturbed point
4. Accept if new C < old C (or with probability exp(-ΔC/T) otherwise)
5. Reduce σ by factor 0.99 each iteration

Temperature schedule: σ₀ = 0.5 (relative to function scale), σ_final = 0.01.
Run for 200-500 anneal iterations. Each inner Adam run: 5,000-10,000 steps.

This is ~10x more total compute than the baseline but expected to give C ≈ 1.503.

**Actionable implication**: For a "full" agent with 150 turns, implement simulated annealing
wrapper around gradient descent. For "explore" agents, focus on the coarse-to-fine pipeline
instead (cheaper).

---

## Finding 5: The Baseline Optimizer Can Be Improved with Simple Hyperparameter Changes

**Relevance**: All solution agents — lowest-effort improvement.

**Detail**:
The baseline (optimize.py) uses:
- `num_steps = 40,000`
- `learning_rate = 0.005`
- `end_value = learning_rate * 1e-4` (= 5e-7, very low)
- Warm-up from 0 to peak: 2,000 steps

**Known issues:**
1. **Too few steps**: 40,000 steps is insufficient for convergence on 600 parameters.
   The related Boyer et al. paper used 1,000,000 gradient steps at similar resolution.
   Increasing to 150,000-200,000 steps alone may drop C from 1.5185 to ~1.510.

2. **Cosine decay kills learning too early**: The cosine schedule ends at 5e-7.
   Better: use `end_value = 1e-5` to maintain some learning late in training.

3. **Adam vs. L-BFGS**: For smooth objectives with moderate parameters (600), L-BFGS
   converges faster than Adam. SciPy's L-BFGS-B can be used after JAX delivers gradients:
   ```python
   from scipy.optimize import minimize
   result = minimize(obj_fn, f0, jac=grad_fn, method='L-BFGS-B',
                     bounds=[(0, None)]*600)
   ```
   This handles non-negativity constraints natively via bounds.

4. **ReLU projection vs. bounds**: The baseline uses `relu(f_values)` post-hoc, meaning
   the optimizer can drive parameters negative (wasted capacity). Use projected gradient
   or L-BFGS-B with bounds=(0,None) for each parameter.

**Actionable implication**: Quick win — increase num_steps to 150,000, raise end_value to
1e-5, and switch to L-BFGS-B with box constraints. Expected C improvement: 1.5185 → ~1.512.

---

## Finding 6: Fourier-Analytic Structure of the Problem

**Relevance**: Research and analytical construction agents — theoretical framework.

**Detail**:
For unit-mass f (∫f = 1), C = max(f★f). In Fourier space:
- Let F(ω) = ∫f(x)e^{-2πiωx}dx (Fourier transform of f)
- Then (f★f)(t) = ∫ F(ω)² e^{2πiωt} dω (inverse FT of F²)
- So C = ||F⁻¹[F(ω)²]||_∞ = ||f★f||_∞

Minimizing C = minimizing the peak of the autoconvolution = minimizing the L∞ norm of F⁻¹[F²].

**Key constraint from non-negativity**: For f ≥ 0, F(0) = 1 and |F(ω)| ≤ 1. The Bochner
theorem implies F is a positive-definite function (in the continuous sense).

**Probabilistic interpretation**: C = peak density of X₁+X₂ where X₁,X₂ are i.i.d. random
variables with density f on [-1/4, 1/4]. Minimizing C = minimizing the peak density of
the sum of two i.i.d. copies — a well-studied problem in probability/information theory.

**Implication for function shape**: The distribution that minimizes the peak density of X₁+X₂
(subject to X₁ ∈ [-1/4,1/4]) is NOT the uniform distribution (which gives C=2) but something
with mass concentrated in a specific pattern.

**Arcsine distribution**: The arcsine distribution f(x) = (1/π)·(1/4-x²)^{-1/2} on [-1/4,1/4]
has interesting autoconvolution properties. Its characteristic function involves Bessel functions.
Worth testing as initialization (see also: Rechnitzer's 2026 ansatz uses (1-4x²)^{-1/2} shape).

**Actionable implication**: Parameterize f in Fourier space (few low-frequency real cosine
coefficients) for a smooth, low-dimensional search space. F(ω) = sum_k a_k cos(2πkx/L)
with non-negativity enforced via projection. Start with k=0...20 (20 parameters), optimize,
then add higher frequencies.

---

## Finding 7: Key Papers and Authors

**Relevance**: Future research agents — literature map.

| Paper | Authors | Year | Key Result |
|-------|---------|------|-----------|
| arXiv:1403.7988 | Cloninger, Steinerberger | 2017 | Lower bound C* ≥ 1.28; interval partition method |
| arXiv:0907.1379 | Matolcsi, Vinuesa | 2010 | Upper bound C* ≤ 1.50992; disproves Schinzel-Schmidt |
| arXiv:0807.5121 | Martin, O'Bryant | 2008 | Earlier bounds; Fourier methods |
| AlphaEvolve paper | Google DeepMind | 2025 | C* ≤ 1.5032; 600-interval step function |
| arXiv:2511.23473 | ThetaEvolve | 2025 | C* ≤ 1.503133; open-source replication |
| arXiv:2602.07292 | Rechnitzer | 2026 | Related L² constant ν₂² to 128 digits |
| arXiv:2506.16750 | Boyer et al. | 2025 | Related L² ratio: 0.901564 via coarse-to-fine |

**Important note**: The Rechnitzer 2026 paper (arXiv:2602.07292) is about the L²-autoconvolution
constant ν₂² ≈ 0.5746, NOT our L∞ problem. Do not confuse the two.

**Where to find AlphaEvolve's function**:
`https://github.com/google-deepmind/alphaevolve_results` → mathematical_results.ipynb, Section B.2.
The notebook contains the exact 600-interval coefficient array achieving C = 1.5032.

---

## Finding 8: Optimization Landscape Properties

**Relevance**: Exploit and genetic agents — understanding convergence behavior.

**Detail**:
- The objective C(f) is **non-convex** in the function values f. Local minima exist.
- The baseline (flat start + Adam) converges to C ≈ 1.518-1.519 — a local minimum.
- Better local minima exist around C ≈ 1.503. Getting there requires escaping.
- The number of local minima grows with N (the resolution). At N=600, there are many.
- **Scale invariance**: C(αf) = C(f). The optimizer should constrain ∫f = 1 to avoid
  ill-conditioning. The baseline's relu post-processing can create a zero-integral function.
- **Gradient structure**: ∂C/∂f_i is proportional to the value of f★f at the argmax
  convolution point. When the peak moves, the gradient changes direction discontinuously.
  This creates "kinks" in the loss landscape.

**Actionable implication**:
1. Always normalize f (divide by ∫f) periodically during optimization to prevent scale drift.
2. Use gradient clipping (max_norm=1.0) to handle gradient spikes when the argmax of f★f moves.
3. For genetic agents: crossover between two good functions by interpolation
   (f_child = α·f_parent1 + (1-α)·f_parent2) works IF both parents are in the same basin.
   Crossover between parents in different basins may be worse than either parent.

---

## Open Questions

1. **What is the true infimum C*?** The gap [1.28, 1.503] is large. Theoretical lower bound
   methods (Cloninger-Steinerberger) have a stated ceiling of 1.276 for their approach.
   New proof techniques are needed for tight lower bounds.

2. **Is the optimal function compactly supported strictly inside [-1/4, 1/4]?**
   Or does it use the full boundary? This affects discretization — should we include f(±1/4)?

3. **Is the optimizer finding a plateau?** C ≈ 1.503 may be a broad flat region in function
   space, with many functions achieving similar C values. Or there may be a narrow attractor.

4. **Does symmetry help or hurt?** Enforcing even symmetry f(x) = f(-x) reduces search space
   by 2×. The Matolcsi-Vinuesa function may or may not be symmetric. Worth testing both.

5. **What happens at N → ∞?** Does C keep decreasing beyond 1.503, or does C plateau
   as N increases beyond 600? The AlphaEvolve answer (600 intervals, 1.5032) might already
   be close to the continuous optimum.
