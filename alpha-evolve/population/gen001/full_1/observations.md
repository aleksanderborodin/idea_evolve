# Observations — gen001_full_1

## Results Summary

| Solution | Fitness | Notes |
|----------|---------|-------|
| sol01.py | 1.5185 | Matched baseline exactly despite Gaussian init + softplus + 80k steps |
| sol02.py | 1.6887 | L-BFGS-B failed — non-smooth max gradient breaks quasi-Newton |
| sol03.py | **1.5108** | Graduated smooth-max + 8 random restarts — best solution |
| sol04.py | 1.5151 | N=800 variant of sol03 — slower, worse |

Baseline: 1.5185. Best: 1.5108. Target: ≤1.5053.

## Core Insight: Smooth Max Is Essential

`jnp.max` returns a one-hot gradient — only the argmax element gets signal. This creates a degenerate optimization where only one grid point updates per step. The rest of the function learns nothing about the peak.

**Fix**: replace `max` with `log-sum-exp(x/T) * T` (smooth-max). With T=0.05 (warm), gradient spreads across all near-max elements. Anneal T down to 0.0003 over training for accurate convergence.

## Why Graduated Annealing Helps

- **High T (0.05)**: very smooth landscape, easy to escape bad basins
- **Medium T (0.003)**: sharper, optimizer refines the shape
- **Low T (0.0003)**: close to true max, final convergence

Multiple temperature phases = curriculum learning for the objective.

## Recommended Next Steps for Exploit Agent

Start from sol03.py's function (1.5108) and:
1. Run 50k more steps at T=0.0001→0.00001
2. Try N=1000 upsampled from sol03's shape
3. Try asymmetric initializations (function not symmetric around 0)
