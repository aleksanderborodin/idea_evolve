# Research Findings — First Autocorrelation Inequality: Mathematical Background

## Summary

The first autocorrelation inequality asks for the minimum constant C such that max(f★f)(t) ≥ C(∫f)² for all non-negative f supported on [-1/4, 1/4]. This is a continuous analogue of the Sidon (B₂) set problem in additive combinatorics. The optimal function must spread autocorrelation energy as uniformly as possible over [-1/2, 1/2]. The gap between the baseline (1.5185) and the target (1.5053) is modest but requires escaping the local minimum the current optimizer is stuck in.

---

## Finding 1: Problem Origin and Known Bounds

**Relevance**: All agents — sets expectations for what improvement is achievable.

**Detail**: The continuous first autocorrelation constant C₁ arises as the continuous limit of the Sidon set problem. In the discrete setting, a B₂ (Sidon) set A ⊂ {1,...,N} satisfies: all pairwise sums a+b are distinct, making 1_A ★ 1_A(t) ≤ 1 for t ≠ 0. The continuous analogue asks for the smallest C such that for ALL non-negative f on [-1/4, 1/4], the autoconvolution is bounded below by C(∫f)².

Known bounds: **1.28 ≤ C ≤ 1.5098**.

- Lower bound C ≥ 1.28: A non-trivial result using Fourier-analytic estimates. The trivial bound is C ≥ 1 (by averaging: total mass of f★f is (∫f)², support has measure 1). The tighter bound uses L²-L∞ inequalities that exploit the constraint that f is supported on an interval of length 1/2.

- Upper bound 1.5098: Achieved by explicit numerical construction. The gap between 1.5098 and the true minimum C* ≥ 1.28 means there is substantial room for improvement beyond C = 1.5098. The target C ≤ 1.5053 is just slightly below the best known upper bound.

**Actionable implication**: The true optimum may be significantly below 1.5053. Agents should not treat 1.5053 as a ceiling — solutions achieving 1.48–1.50 are plausibly reachable. Push hard.

---

## Finding 2: Why C ≥ 1 Is Tight and Why 1.28 Is Non-Trivial

**Relevance**: Explore/research agents — explains why the optimization is hard.

**Detail**:

Trivial lower bound: Since ∫₋₁/₂^{1/2} (f★f)(t) dt = (∫f)² and the support of f★f is [-1/2, 1/2] (measure 1), by averaging: max_t (f★f)(t) ≥ (∫f)². This gives C ≥ 1.

The tighter bound C ≥ 1.28 exploits the L²-norm constraint. For f supported on [-1/4, 1/4] (measure 1/2), by Cauchy-Schwarz:

    (∫f)² ≤ (1/2) * ∫f²

So ∫f² ≥ 2(∫f)². For even f (f(x) = f(-x)):

    f★f(0) = ∫f(x)f(-x)dx = ∫f(x)²dx ≥ 2(∫f)²

This would give C ≥ 2 for even functions — but this is wrong because f★f(0) is not necessarily the maximum! For even functions, the maximum of f★f can occur at t ≠ 0. The bound C ≥ 1.28 accounts for this by tracking the interplay between f★f at t=0 and other values.

**Key insight**: For an even function, f★f is also even and is largest at t=0 *only if* f is unimodal (single peak). For bimodal f (two bumps), the maximum of f★f can shift to a non-zero lag, allowing f★f(0) to be smaller than ∫f². This is why bimodal functions can achieve lower C than unimodal ones.

**Actionable implication**: Two-bump (bimodal) initializations for optimization are theoretically motivated. A function with two bumps at positions ±a can have its autoconvolution peak away from t=0, potentially achieving lower C.

---

## Finding 3: Optimal Function Properties

**Relevance**: All solution-writing agents (explore, exploit, full).

**Detail**: Based on the structure of the problem and analogy with discrete Sidon constructions:

1. **Symmetry**: The extremal function is almost certainly **even** (f(x) = f(-x)). The problem is symmetric under reflection x → -x, so breaking symmetry cannot help. Any non-symmetric solution f has an even counterpart (f(x) + f(-x))/2 with the same ∫f and lower or equal max(f★f) (by triangle inequality for convolution).

2. **Support**: The optimal function likely does NOT use the full domain [-1/4, 1/4]. The endpoints contribute to the autoconvolution at large lags t ≈ ±1/2, which are "free" (the autoconvolution there is small). Concentrating mass in the interior wastes this opportunity. However, having mass at the extreme endpoints (x ≈ ±1/4) contributes a large cross-term to f★f(0). The optimal support balance is non-trivial.

3. **Profile shape**: Based on analogies with known Sidon-type constructions, the optimal function likely has a **two-bump** or **plateau-with-dip** structure. Specifically:
   - Two bumps of width ~a at positions ±b, with a and b chosen to spread the autoconvolution peak
   - Or a flat plateau with a dip in the middle (the "W-shape")
   - The baseline's flat box initialization converges to a single-bump solution that is not globally optimal

4. **The autoconvolution of two bumps**: If f = A * 1_{[b-a, b+a]} + A * 1_{[-b-a, -b+a]} (two symmetric rectangular bumps of width 2a, separation 2b):
   - f★f has peaks at t = 0 (self-convolution of each bump): height ~ 2A²(2a)
   - f★f has peaks at t = ±2b (cross-convolution): height ~ A²(2a)
   - The max is at t=0 (if 2b > 2a): max ~ 2A²(2a) = 2A²·(half-bandwidth)
   - ∫f = 4Aa
   - C = 2A²(2a) / (4Aa)² * dx = 2(2a) / (16a²) * (1/dx)... (need to use continuous formula)

   In continuous form: C = max(f★f) / (∫f)² = 2A²·2a·1 / (4Aa)² = 4A²a / 16A²a² = 1/(4a)

   For the two-bump function, a = bump half-width. Bumps of width 1/4 each, total support 1/2 → C = 1/(4·(1/8)) = 2. Same as uniform! But with SEPARATION between bumps, the cross-term occurs at a DIFFERENT lag and the self-term peak is smaller:

   More careful analysis: For bumps of half-width a separated by distance 2b (center-to-center):
   - f★f(0) = ∫f(x)f(-x)dx = 2 * (2a) * A² = 4A²a (self-terms only if b+a < 1/4)
   - f★f(2b) = cross-term height = A² * min(2a, 2a) * ... depends on geometry
   - If b is chosen so that cross-terms don't overlap with self-terms: max(f★f) is lower

   Example: Two bumps of width w at ±(1/4-w/2), so they fill the edges:
   - w+w = 2w ≤ 1/2 → w ≤ 1/4
   - Cross-term at lag ≈ 1/2-w
   - For w = 1/4: bumps are [0, 1/4] and [-1/4, 0] → this is just the uniform case
   - For w < 1/4: the self-convolution peak at t=0 is smaller

5. **Three or more bumps**: With 3+ symmetric bumps, the cross-terms multiply and the autoconvolution structure becomes more complex. This may further reduce C, analogous to larger Sidon sets in the discrete case.

**Actionable implication**:
- Always enforce symmetry: optimize f on [0, 1/4] only, then mirror. This halves search space and avoids asymmetric local minima.
- Initialize with two symmetric bumps at ±(1/4 - ε) rather than a flat box.
- Try initialization with 3 bumps (near ±1/4 and at 0 with smaller weight).

---

## Finding 4: Non-Convexity and the Optimization Landscape

**Relevance**: Explore, exploit, genetic agents — informs optimizer choice.

**Detail**: The objective C(f) = max(f★f) / (∫f)² is **not convex**. The `max` operation in the numerator creates non-differentiable regions, and the ratio structure creates saddle points. The optimization landscape has:

1. **Multiple local minima**: The baseline converges to C ≈ 1.5185, but better local minima exist (the bound 1.5098 was found by other methods). Different initializations will converge to different local optima.

2. **Symmetry-related degeneracy**: Any translate of an optimal function (f(x+δ)) achieves the same C. This creates flat directions in parameter space that slow gradient descent.

3. **The ReLU gradient issue**: The baseline code applies ReLU at the end: `f_values_final = jax.nn.relu(f_values)`. But during training, values can go negative, at which point the effective gradient through ReLU is zero — the optimizer cannot pull these values back up. This means the optimizer effectively "prunes" grid points that go negative, reducing the search space mid-optimization. Better parameterizations:
   - `f = softplus(g)` (differentiable everywhere, f > 0 always)
   - `f = g²` (differentiable, non-negative, but has gradient vanishing issue at 0)
   - `f = exp(g)` (always positive, full gradient signal, but f never reaches 0 exactly)

4. **The max is a non-smooth objective**: The `max` over the autoconvolution is non-differentiable when the maximum moves between positions. JAX differentiates through max with a subgradient, but this can cause gradient discontinuities. Consider smoothing: `C_smooth = log(sum(exp(k * conv))) / k` for large k (log-sum-exp approximation).

5. **Resolution matters**: With N=600 grid points, dx = 0.5/600 ≈ 8.3e-4. The autoconvolution peak can be as sharp as dx, so fine features require high N. But N=600 is probably sufficient for finding the optimal shape — the true optimal function is likely smooth.

**Actionable implication**:
- Replace ReLU with softplus parameterization: `f = jax.nn.softplus(g)` in training
- Try multiple random initializations and pick the best
- Use L-BFGS-B (available in scipy.optimize) which handles this kind of smooth constrained problem well and often outperforms Adam for this type of functional optimization
- Consider symmetry-enforced optimization: only optimize on half-domain, mirror for evaluation

---

## Finding 5: Spectral Interpretation — What Makes a Good Function

**Relevance**: All agents building intuition about what to optimize toward.

**Detail**: The autoconvolution f★f has Fourier transform |F̂(f)(ω)|². To minimize max(f★f), we want f★f to be as FLAT as possible on its support [-1/2, 1/2], i.e., |F̂(f)(ω)|² should be approximately constant as a function of ω.

A function with flat Fourier power spectrum |F̂(f)|² = constant is called "spectrally flat" or "white." Non-negative functions cannot be perfectly spectrally flat (a non-negative function has F̂(f)(0) = ∫f > 0 while a white-noise process has equal power everywhere), but approximately flat spectra are achievable.

**Approximate spectral flatness implies low C**:
- If |F̂(f)(ω)|² ≈ c for ω ∈ [-B, B] and ≈ 0 outside:
  - f★f ≈ c * 1_{[-1/B, 1/B]} (approximately box function)
  - If B is large enough that 1/B < 1/2, this is a flat box → max ≈ c, support ≈ 1/B
  - But ∫f★f = (∫f)² = c * (2/B), so max ≈ (∫f)² / (2/B) = B(∫f)²/2
  - C ≈ B/2 ... this increases with bandwidth! The spectral argument goes the other way.

Wait — actually to MINIMIZE max(f★f), we want f★f to be as SPREAD OUT as possible (large support), not concentrated. If f★f is perfectly flat on [-1/2, 1/2] (measure 1), then max(f★f) = (∫f)²/1 = (∫f)², giving C = 1 (the lower bound). So the goal is NOT spectral flatness of f — it's flatness of f★f itself.

f★f is flat (≈ constant on [-1/2, 1/2]) when f "looks like" a sample from a uniform random phase process on [-1/4, 1/4]. In practice: non-negative functions with dispersed, irregularly-spaced support tend to have flatter f★f.

**Actionable implication**:
- Functions with multiple, irregularly spaced bumps (not evenly spaced, not symmetric spacing) can have flatter f★f, potentially achieving lower C
- The regular two-bump structure (finding 3) is a good start; asymmetric three-bump placement may do better
- "Pseudo-random" support structures inspired by discrete Sidon sets (e.g., {0, 1, 3, 7} mod some scale) could be good initializations

---

## Finding 6: Connection to Sidon Sets — Lifting Discrete Constructions

**Relevance**: Explore agents trying novel initializations.

**Detail**: In the discrete setting, a Sidon (B₂) set A ⊂ {0,1,...,N-1} satisfies: all pairwise sums a_i + a_j (i ≤ j) are distinct. The key property: 1_A ★ 1_A(t) ≤ 1 for all t ≠ 0, and 1_A ★ 1_A(0) = |A| (maximum at 0).

Known small Sidon sets (and their relative positions in [0, 1]):
- {0, 1, 3, 6}: all pairwise sums distinct (Sidon)
- {0, 1, 3, 7, 12, 20, 30}: larger Sidon set
- Perfect difference sets from finite fields: if p is prime, the quadratic residues mod p form a "near-Sidon" set

**Lifting to continuous functions**: Take a Sidon set A = {a₁ < a₂ < ... < aₖ} ⊂ [0, M] and define:
    f(x) = sum_{i} gaussian(x - a_i/M * (1/2) - 1/4, σ)

Scale to fit [-1/4, 1/4]. The parameter σ controls how smooth the bumps are (wider σ = more overlap, more like continuous limit; narrower σ = more spike-like, closer to discrete Sidon).

For the 4-element Sidon set {0,1,3,6}, placing bumps at x ∈ {-1/4, -1/12, 1/12, 11/36} might give a reasonable starting point. The autoconvolution of this function will have many small peaks at distinct lags (Sidon property) rather than one large peak.

**Caveat**: The minimum C construction in the continuous setting is not simply the continuous limit of the discrete Sidon set. The optimal continuous function minimizes C over ALL non-negative functions, which is a different optimization than finding the densest Sidon set. But Sidon-inspired initializations provide good starting points for gradient descent.

**Actionable implication**: Try initializing with Gaussian bumps placed at relative positions inspired by small Sidon sets:
- 2 bumps: {0, 1} → at x = {-1/4, 1/4} (but these are endpoints, less ideal)
- 2 bumps: {0, 1} → at x = {-1/8, 1/8} with σ ≈ 0.04
- 4 bumps at {0,1,3,6}/6 → at x = {-1/4, -1/12, 1/12, 5/12}... need to rescale to [-1/4, 1/4]
  = {-1/4, -1/4 + 1/6 * (1/2), -1/4 + 3/6 * (1/2), -1/4 + 6/6 * (1/2)} = {-1/4, -1/6, 0, 1/4}
  This is 4 bumps at x ≈ -0.25, -0.167, 0, 0.25. Worth trying with σ ≈ 0.03-0.05.

---

## Finding 7: Practical Optimization Strategies

**Relevance**: Explore/full/exploit agents implementing solutions.

**Detail**: Based on the mathematical structure:

**1. Reparameterize for unconstrained optimization**:
```python
# Instead of: f = relu(g)
# Use: f = softplus(g) = log(1 + exp(g))
# Or:  f = g**2  (but has zero-gradient at g=0)
# Best: f = exp(g)  (strictly positive, full gradients)
g = jnp.zeros(N)  # optimize g, f = exp(g)
```

**2. Enforce symmetry explicitly**:
```python
N_half = N // 2
g_half = params  # only N/2 free parameters
g_full = jnp.concatenate([g_half[::-1], g_half])  # symmetric
f = softplus(g_full)
```
This halves parameter count and forces even symmetry, which the optimal function almost certainly has.

**3. Better initializations to try** (all should be implemented and run, picking best):
- Two symmetric Gaussians: f(x) = exp(-((x ± 0.15)/0.04)²)
- Wide center + narrow wings: f(x) = exp(-(x/0.12)²) + 0.3*(exp(-((x-0.2)/0.03)²) + exp(-((x+0.2)/0.03)²))
- Cosine-squared: f(x) = cos(πx * 2)² (non-negative on [-1/4, 1/4])
- Flat box (current baseline): uniform 1 on middle half
- Sidon-inspired 4-bump: bumps at x ≈ {-0.25, -0.167, 0, 0.25}

**4. Try L-BFGS instead of Adam**:
```python
from scipy.optimize import minimize
result = minimize(lambda g: float(compute_c(softplus(g))),
                  g0, method='L-BFGS-B',
                  jac=lambda g: np.array(jax.grad(lambda g: compute_c(softplus(g)))(g)))
```
L-BFGS uses second-order information and often converges faster and to lower minima for smooth objectives.

**5. Multi-start strategy**: Run gradient descent from 5-10 different initializations, keep the best. The optimization is fast enough per run that multi-start is practical.

**6. Resolution staircase** (idea_004): Start at N=100, optimize to convergence, upsample to N=300, refine, upsample to N=1000. This finds the right shape cheaply at low resolution then refines it.

**7. Smooth max objective**: Replace `jnp.max(conv)` with a smooth approximation to avoid subgradient instability:
```python
def smooth_max(x, beta=100.0):
    return jnp.log(jnp.sum(jnp.exp(beta * (x - jnp.max(x))))) / beta + jnp.max(x)
```

**Actionable implication**: The single most important change is reparameterization (softplus/exp) and enforcing symmetry. These two changes address the two biggest known deficiencies in the baseline. After that, multi-start with diverse initializations is most likely to improve C below 1.5053.

---

## Finding 8: The Critical Computation Detail

**Relevance**: All agents — avoid a subtle bug.

**Detail**: The helper.py computes:
```python
padded_f = jnp.pad(f_non_negative, (0, N))  # pads ONLY on right
fft_f = jnp.fft.fft(padded_f)
conv_f_f = jnp.fft.ifft(fft_f * fft_f).real
scaled_conv = conv_f_f * dx
max_conv = jnp.max(scaled_conv)
```

This computes the **circular convolution** of padded_f with itself, which gives the **linear autoconvolution** of f with itself (since f is supported on [0, N-1] and padding to 2N prevents aliasing). The output has length 2N and is valid.

However, the maximum is taken over ALL 2N values, including positions corresponding to lags t ∈ [1/4, 3/4] of the full domain. For f supported on [-1/4, 1/4], the autoconvolution is supported on [-1/2, 1/2]. In the discretized version, the linear convolution at output index k corresponds to lag t = (k - N/2 + something) * dx. Some output indices (near the "wrap" of the circular convolution) may contain numerical artifacts.

**Critical**: For symmetric f, the maximum should be at or near t=0, corresponding to the "center" of the linear convolution output. If your solution gets a surprisingly low C, verify that the maximum isn't an artifact from a wrap-around position.

In practice, for reasonable f, this is not an issue — the constraint `max_conv` takes the true maximum of the linear autoconvolution, which is physically meaningful. Just be aware of this when debugging unexpected behavior.

**Actionable implication**: When debugging solutions, print the argmax of conv_f_f to verify the peak position is physically sensible (should be near N//2 for symmetric functions).

---

## Open Questions

1. **What specific function achieves the current best C ≈ 1.5098?** If we could access the shape of this function (from whatever paper computed this bound), it would be an ideal starting point. The fact that C_best = 1.5098 exists means it's achievable by a specific, likely smooth and symmetric function.

2. **Is there a closed-form for the extremal function?** In some related problems (e.g., Bernstein's inequality, Chebyshev polynomials), extremal functions have elegant closed forms. The first autocorrelation extremal function might be expressible as a finite combination of B-splines or cosines.

3. **What is the exact lower bound C ≥ 1.28?** The proof technique would directly suggest which function shapes are farthest from the lower bound and might indicate what an extremal function looks like.

4. **Does the extremal function have zeros on (-1/4, 1/4)?** The optimal function might vanish on some subset of the domain (it could be supported on a proper closed subset of [-1/4, 1/4]). This would mean the optimal support is a strict subset, guiding discretization.

5. **Multi-bump count**: How many bumps does the optimal function have? Two symmetric bumps, three (two outer + one center), or more? This determines which initializations to prioritize.

6. **Is C_opt the same as the "Sidon constant" in the analytic literature?** There may be published numerical values or bounds in papers by Green, Tao, or Bourgain that give a sharper target.
