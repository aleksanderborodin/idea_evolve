# Research Agent Debrief — Gen 001, research_1

## Task

Research the mathematical background of the First Autocorrelation Inequality and produce a findings report. No solution code was required.

## Work Completed

Produced `findings.md` with 8 detailed findings covering:

1. **Problem origin and known bounds** (1.28 ≤ C ≤ 1.5098). The target C ≤ 1.5053 is just below the best known upper bound. The true optimum may be significantly lower (possibly 1.48–1.50).

2. **Why the trivial lower bound C ≥ 1 exists and how C ≥ 1.28 is proved** via L²-L∞ Cauchy-Schwarz argument. Key insight: bimodal (two-bump) functions can shift the autoconvolution peak away from t=0, enabling lower C than unimodal functions.

3. **Optimal function properties**: Almost certainly even-symmetric, likely two-bump or W-shaped, probably does not use the full domain uniformly. Three or more bumps may further reduce C.

4. **Optimization landscape**: Non-convex, multiple local minima. Identified two key deficiencies in the baseline: (a) ReLU parameterization kills gradient signal for negative values; (b) no symmetry enforcement doubles parameter space. Recommended softplus/exp reparameterization and explicit symmetry enforcement.

5. **Spectral interpretation**: The goal is to make f★f as flat as possible on [-1/2, 1/2]. Functions with dispersed, irregularly-spaced support produce flatter autoconvolution.

6. **Sidon set connection**: Discrete Sidon sets like {0,1,3,6} can be lifted to Gaussian bumps on [-1/4, 1/4] as initializations. These provide good starting points for gradient descent because they naturally produce flat autoconvolution.

7. **Practical optimization strategies**: Softplus/exp reparameterization, symmetry-enforced half-domain optimization, multi-start with 5–10 initializations, L-BFGS instead of Adam, resolution staircase (N=100 → 300 → 1000), smooth-max objective (log-sum-exp).

8. **Computation details and potential bugs**: The helper.py FFT computation is correct; the padding prevents aliasing. For symmetric f, the argmax should be near the center of the output array — a useful debugging check.

## Key Recommendations for Other Agents

- **Most impactful single change**: Replace `relu(g)` with `softplus(g)` or `exp(g)` parameterization AND enforce even symmetry (optimize on [0, 1/4] only, mirror).
- **Best initializations**: Two symmetric Gaussians at ±0.15 (σ≈0.04), Sidon-inspired 4-bump at {-0.25, -0.167, 0, 0.25}, wide center + narrow wings.
- **Best optimizer**: L-BFGS (scipy.optimize.minimize with JAX gradients) often outperforms Adam for this type of smooth functional optimization.
- **Run multi-start**: At least 5 initializations per optimization run; take the best.

## Output Files

- `findings.md`: Full research report with 8 findings and actionable implications for solution agents.

## Result

Research task complete. No solution code was produced (as directed). All findings are in `findings.md`.
