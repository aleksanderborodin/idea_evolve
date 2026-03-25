# gen001_full_1 Debrief Report

## Solution Scores

| File | Fitness | Valid | Approach |
|------|---------|-------|----------|
| sol01.py | 1.5185 | 1 | N=1000, Gaussian bump init, softplus reparameterization, 80k steps, 3 restarts (seeds 42/123/7) |
| sol02.py | 1.6887 | 1 | scipy L-BFGS-B, N=800, 5 initializations (gaussian/flat/cosine/triangle), bounds=[0,inf] |
| sol03.py | **1.5108** | 1 | **BEST** — graduated smooth-max (log-sum-exp, T=0.05→0.0003), 8 random restarts, N=600, softplus |
| sol04.py | 1.5151 | 1 | Same as sol03 but N=800, T→0.0001, 12 restarts, 84k steps/restart — slower convergence at higher N |

Baseline: **1.5185**. Best achieved: **1.5108** (sol03). Target: ≤1.5053.

## What Worked

- **Graduated smoothing** (log-sum-exp approximation to max, annealing temperature 0.05→0.0003): big win. The true `jnp.max` only passes gradient to the single argmax element, starving other points. log-sum-exp spreads gradient across near-max elements, enabling escape from the 1.5185 basin.
- **Softplus reparameterization**: ensures f>0 always, no dead-gradient regions from relu.
- **Random restarts with diverse initializations**: critical — different init shapes (Gaussian at different locations, raised cosine, flat window) find different basins.

## What Did NOT Work

- **Sol01 (N=1000, Gaussian init, softplus, 80k steps, 3 restarts)**: Converged to 1.5185 — same as baseline. Despite Gaussian initialization and softplus, the optimization still found the same local minimum. Higher N alone doesn't help.
- **Sol02 (L-BFGS-B)**: 1.6887 — worse. L-BFGS-B without the smooth-max couldn't navigate the non-smooth landscape. The sparse gradient from true max derailed it.
- **Sol04 (N=800 version of sol03)**: 1.5151 — slightly worse than sol03 at N=600. Higher resolution slows each step, reducing effective exploration in the same wall-clock time.

## Key Findings

1. **The 1.5185 basin is sticky**: All standard Adam + various inits converge there. Breaking out requires the smooth-max trick.
2. **True max kills gradient flow**: jnp.max gradient is one-hot — only the single peak element learns. log-sum-exp is essential.
3. **N=600 outperformed N=800/1000**: Fewer parameters → faster steps → more exploration in fixed time. May need longer runs at higher N.
4. **Target 1.5053 not reached**: sol03 achieves 1.5108, still 0.005 above target.

## What I Lacked

- Knowledge of the theoretical optimal function shape (literature on first autocorrelation inequality / Sidon sets)
- A good warm-start from the sol03 solution with continued optimization at lower temperatures
- More wall-clock time to run more restarts or longer phases

## Specific Experiments to Run

1. **Continue sol03 from its best checkpoint**: resume with T=0.0001→0.00003 for another 50k steps
2. **Asymmetric initializations**: the theoretical bound 1.28 may require non-symmetric f; try skewed initializations
3. **Higher N starting from sol03's shape**: upsample sol03's function to N=1200, then fine-tune
4. **Lower temperature floor**: try T=0.00001 (nearly true max) — may converge to better solution
5. **Exploit agent**: take sol03 (1.5108) and push it with a dedicated fine-tuning session

## Surprises

- L-BFGS-B, normally excellent for smooth bounded optimization, performed worst (1.6887). The non-smooth max makes it unstable without the smoothing trick.
- Sol01 with 3× restarts at N=1000 still found 1.5185 exactly — strongly suggests a very wide attractor basin for this value.
- The graduated smoothing idea worked immediately on first try (sol03), jumping from 1.5185 to 1.5108 with N=600 and only 8 restarts.
