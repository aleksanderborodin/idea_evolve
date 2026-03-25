# Debrief Report — Explore Agent 2, Generation 1

## Solution Scores

| Solution | Fitness (C) | Valid | Approach |
|----------|-------------|-------|----------|
| sol01    | 3.0000      | 1     | Raised cosine (Hann window), purely analytical |
| sol02    | 1.5729      | 1     | Asymmetric ramp init, Adam 50k steps |
| sol03    | 1.5249      | 1     | Best of 5 asymmetric inits, Adam relu 40k each |
| sol04    | 1.5294      | 1     | Fourier-basis parameterization, Adam 60k |
| sol05    | 1.5730      | 1     | Multi-scale coarse-to-fine, Adam |
| sol06    | 1.5278      | 1     | 3 asymmetric seeds × 35k+35k, softplus |
| sol07    | 1.5801      | 1     | Gaussian mixture K=8, Adam 80k |
| sol08    | 1.5207      | 1     | Lion 60k + Adam 50k, symmetric box init |
| sol09    | **1.5182**  | 1     | Best of 4: Lion 50k + Adam 70k, symmetric box |

**Best: sol09 at C=1.5182** (target: ≤ 1.5053, baseline: 1.5185)

## What I Tried

### 1. Pure Analytical Constructions
**Hann window (sol01, C=3.0):** The raised cosine f(x)=0.5(1+cos(4πx)) is smooth and compact but gives C=3.0. This is because symmetric functions satisfy C ≥ 2 (proven via Cauchy-Schwarz: ||f||_2² ≥ 2(∫f)² for f on [-1/4,1/4]). The Hann window is more concentrated than a box, so C is even higher.

### 2. Asymmetric Initialization Strategy
**Key discovery:** Symmetric functions can never achieve C < 2. The optimizer must find an asymmetric solution. Starting asymmetrically (mass concentrated on [0,1/4] with a ramp) allows breaking below C=2 on the first optimization run.
- sol02: Simple ramp, 50k steps → C=1.5729
- sol03: Best of 5 asymmetric seeds → C=1.5249

### 3. Structured Parameterizations
- **Fourier basis (sol04):** Used cosine+sine modes (asymmetric capable), C=1.5294. Not better than direct parameterization.
- **Gaussian mixture (sol07):** Learnable positions/widths/heights, K=8, C=1.5801. Over-parameterized, hard to optimize.

### 4. Multi-Scale
- **Coarse-to-fine (sol05):** N=100→600→1200, C=1.5730. Cubic upsampling loses shape fidelity.

### 5. Better Optimizers
- **Lion + Adam combo (sol08, sol09):** Lion optimizer with sign-gradient updates escapes plateaus better. Best of 4 seeds with Lion 50k + Adam 70k gives C=1.5182.

## Mathematical Insights Discovered

1. **C ≥ 2 for all symmetric functions** on [-1/4, 1/4]. This is a hard mathematical barrier.
2. **The optimal function is strongly asymmetric** — essentially a bump/ramp on one side of the domain.
3. **More optimizer steps always help** (diminishing returns but real progress), confirming the landscape is not trapped in bad local minima at our scale.
4. **Lion > Adam** for this objective in the same step budget.

## What Information I Lacked

- The analytical shape of functions known to achieve C ≈ 1.28 (theoretical best) or C ≈ 1.50 (state of art)
- Whether any specific initialization (beyond asymmetric) is known to be near-optimal
- What N (resolution) is sufficient for the true optimum

## What Might Be Wrong

- My analysis that "symmetric C ≥ 2" assumes the max of f*f is at t=0 for symmetric f, which is always true when f ≥ 0 and symmetric. This appears verified.

## State of Affairs Accuracy

No state of affairs existed for gen 1 (first generation). Nothing misleading.

## What I'd Do Differently

- Try L-BFGS or conjugate gradient for final fine-tuning (second-order methods converge faster near optima)
- Run 200k+ steps from the Lion-warmed solution
- Investigate the mathematical literature for the known optimal function structure
- Try higher resolution N=2000 with good init

## Specific Experiments to Run

1. **L-BFGS fine-tuning**: Take the best found solution and run scipy.optimize.minimize with L-BFGS-B for 10k function evaluations — likely gets below 1.505.
2. **Longer Lion+Adam**: 200k total steps from symmetric box, track best-ever seen.
3. **N=2000 experiment**: Does higher resolution change the optimal shape?
4. **Anneal-then-descent**: Add Gaussian noise scaled to 0.01× current values every 10k steps to escape local minima.

## Surprises

- The symmetric box init (baseline approach) converges better than explicit asymmetric starts. The optimizer apparently breaks symmetry more efficiently when starting from a symmetric point (steepest descent direction is along the asymmetry).
- sol09 (C=1.5182) barely beats the baseline (C=1.5185) despite 3× more compute. Diminishing returns are severe near C≈1.52.
- The Gaussian mixture (sol07, C=1.5801) is much worse than a direct parameterization — adding structure via the Gaussian basis seems to hurt optimization.
