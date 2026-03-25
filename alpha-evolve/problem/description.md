# First Autocorrelation Inequality — Functional Optimization

## Challenge
Functional optimization in analysis. Find a non-negative function f: R → R that minimizes the constant C in the inequality max_{-1/2≤t≤1/2} (f ★ f)(t) ≥ C (∫_{-1/4}^{1/4} f(x) dx)².

**Target: C ≤ 1.5053** (lower is better)

## Objective
Return a discretized non-negative function f: R → R such that:
1. **(Non-negativity)** All function values are non-negative: f(x) ≥ 0 for all x
2. **(Finiteness)** All values are finite real numbers (no NaN or infinity)
3. **(Non-triviality)** Function is not identically zero (∫f > 0)
4. **(Minimality)** The constant C = max(f ★ f) / (∫f)² is minimized

## Output Format
Implement `def entrypoint():` that returns a 1D NumPy array:
- Shape: (N,) array of non-negative function values
- Represents f evaluated on uniform grid over [-1/4, 1/4] (grid spacing inferred from array length)
- Use numpy, jax, scipy, or standard library as needed
- Fix random seeds if using randomness (e.g., jax.random.PRNGKey(42))
- Return type: np.ndarray with dtype float, shape (N,)

## Scoring
- **Fitness (primary):** C — the autocorrelation constant. **LOWER IS BETTER.**
- **Valid:** 1 if all constraints pass, 0 otherwise.
- Goal: fitness ≤ 1.5053
- Known bounds: 1.28 ≤ C ≤ 1.5098

## Failure Modes to Avoid
- Zero or near-zero functions (C undefined due to division by zero)
- Functions with concentrated mass creating high autoconvolution peaks
- Insufficient discretization resolution missing optimal function shapes
- Numerical instabilities from FFT precision

## Helper Functions
- `helper.py` provides `compute_c(f_values)` → float (JAX-based, differentiable)
  - Input: (N,) array of non-negative function values on domain [-1/4, 1/4]
  - Computes autoconvolution (f ★ f) via FFT
  - Returns C = max(f ★ f) / (∫f)²

## Problem Complexity
This is a non-convex functional optimization problem in high-dimensional space. The objective involves finding the maximum of autoconvolution normalized by squared integral, creating complex interactions between function shape and convolution structure. The problem arises in additive combinatorics (Sidon sets) and requires balancing autoconvolution peak height with integral magnitude.

## Initial Programs
- `problem/initial_programs/optimize.py`: JAX + optax gradient descent baseline
