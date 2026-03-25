# Observations — Explore Agent 2, Generation 1

## Core Mathematical Insight

**Symmetric functions cannot achieve C < 2.** For symmetric f (f(x)=f(-x)), the autoconvolution at t=0 equals ||f||_2^2, and by Cauchy-Schwarz ||f||_2^2 >= 2*(integral f)^2. So C >= 2 for all symmetric functions. This means:
- The Hann window (symmetric) gives C=3.0 — worse than a flat box (C=2.0)
- The optimal function MUST be asymmetric

**Breaking symmetry is the key mechanism.** When f is asymmetric, (f*f)(0) can be small because the function doesn't overlap well with its reflection. The autoconvolution peak shifts to some t != 0, potentially allowing C < 2.

## What Was Tried

### Pure analytical (no optimization)
- **sol01** (Hann window): C=3.0. Symmetric — exactly as predicted, C >= 2.

### JAX optimization with asymmetric initialization
- **sol02** (ramp on right half, 50k Adam): C=1.5729. Asymmetric init breaks the C>=2 barrier immediately. Confirms the theory.
- **sol03** (best of 5 asymmetric inits, each 40k Adam relu): C=1.5249. Multi-start helps.
- **sol04** (Fourier basis with sine modes, 60k Adam): C=1.5294. Structured parameterization doesn't help vs direct.

### Multi-scale approaches
- **sol05** (coarse-to-fine N=100->600->1200): C=1.5730. Worse — cubic upsampling loses important shape details.

### Extended runs with symmetric box init
- **sol06** (3 asymmetric seeds × 35k + 35k softplus): C=1.5278. Softplus slightly worse than relu here.
- **sol07** (Gaussian mixture K=8, 80k): C=1.5801. Over-parameterized mixture is hard to optimize.
- **sol08** (Lion 60k + Adam 50k, symmetric box, best-tracking): C=1.5207. Lion optimizer helps!
- **sol09** (4 seeds × Lion 50k + Adam 70k, best-of-4): C=1.5182. Best result, very close to baseline (1.5185).

## Key Findings

1. **Asymmetric init is necessary but not sufficient** for beating the symmetric box + Adam baseline. The symmetric box init (like baseline) with Lion+Adam actually converges better than explicit asymmetric starts.

2. **Lion optimizer outperforms Adam** for this objective. It converges faster and to better minima in same step budget.

3. **More steps help**: sol08 (110k steps) > sol06 (70k) > sol02 (50k). Diminishing returns but still improving.

4. **The global optimum shape is roughly**: a function with mass concentrated on one side of [-1/4, 1/4], nearly zero on the other side. The exact optimal shape looks like an asymmetric bump with a specific tail.

5. **The target (1.5053) requires something beyond Adam/Lion + random init**. Our best (1.5182) is close to the baseline (1.5185). Need either:
   - Much longer runs (200k+ steps)
   - Smarter initialization from mathematical insight
   - Different optimizer (e.g., L-BFGS for fine-tuning)
   - Higher resolution (N=2000+)

## Unexplored Directions

- **L-BFGS / second-order methods**: Near the optimum, Newton-type methods converge faster than first-order.
- **Simulated annealing or evolutionary methods**: To escape local minima.
- **Analytical constructions from Sidon set theory**: The true optimum (~1.28) likely has a specific number-theoretic structure.
- **Reparameterization via log(f)**: Would enforce strict positivity and may have better gradient landscape.
- **Mixed-resolution upsampling**: Start coarse, optimize, upsample, fine-tune — but needs better interpolation than cubic spline.
