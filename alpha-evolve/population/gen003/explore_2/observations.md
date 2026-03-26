# Observations — gen003_explore_2

## Summary of Results

| Solution | Fitness (C) | Approach |
|----------|-------------|----------|
| sol01    | 1.508974    | 3 init families × 2 seeds — arcsine winner |
| sol02    | 1.510186    | Arcsine deep-dive, 10 subinterval configs |
| sol03    | 1.509114    | Arcsine 3-stage pipeline (N=80→200→600), 12 seeds |
| sol04    | 1.509226    | 25 coarse seeds (arcsine+gauss+comb) → top-5 fine |

**Best this session: sol01 at C = 1.508974** (beats prior best of 1.5091).

---

## What I Tried

### sol01 — 3-family initialization comparison (3 families × 2 seeds)
**Families tested:** Comb (narrow asymmetric peaks), Step function (8 piecewise-constant segments), Arcsine-weighted (1/sqrt((x-a)(b-x)) on a subinterval).

**Per-family results:**
- Comb best: 1.515444
- Step best: 1.519498
- Arcsine best: **1.508974** (seed 0: subinterval a=-0.05, b=0.22, positive tilt)

**Key finding:** Arcsine initialization on [-0.05, 0.22] with positive tilt (0.1→0.5) found C=1.508974, beating the prior best of 1.5091 from Gaussian-bump inits. The arcsine creates a U-shaped profile (peaks at interval endpoints) — a natural asymmetric bimodal initialization. The positive-biased subinterval [-0.05, 0.22] concentrates mass in the positive half of the domain.

### sol02 — Arcsine family deep-dive (10 subinterval configs)
Varied (a, b) and tilt direction systematically. Best config: a=-0.22, b=0.05, tilt=-1 (mirror of sol01 winner) → C=1.510186. Notably, replicating the exact sol01 winner parameters with a different noise key gave C=1.5115 (worse). The result is noise-key sensitive.

### sol03 — 3-stage pipeline on arcsine family (12 seeds)
Added intermediate N=200 stage between coarse and fine. 12 configs varying (a, b, tilt) around the winning region. Best: C=1.509114 (a=-0.05, b=0.22, tilt=0.08→0.45). The 3-stage pipeline did not consistently improve over the 2-stage approach.

### sol04 — 25-seed funnel (coarse sweep → top-5 fine)
Ran 25 short coarse explorations (12 arcsine + 8 Gaussian + 5 comb), kept top-5 coarse solutions, ran full fine on each. All top-5 coarse solutions were from the arcsine family (Gaussian and comb failed to rank in top-5 at coarse level). Best fine: C=1.509226.

---

## What Worked

1. **Arcsine initialization beats Gaussian bumps** at coarse scale, and this advantage survives to fine. All top-5 coarse solutions in sol04 were arcsine-initialized.

2. **Subinterval biased to one side** (either positive or negative half of domain) works better than centered or full-domain arcsine. The best performers were a=-0.05, b=0.22 (positive bias) and a=-0.22, b=0.05 (mirror).

3. **2-stage pipeline (N=80→600)** is competitive with 3-stage (N=80→200→600). The intermediate resolution stage adds computation without consistent improvement.

4. **Warm fine stage** (starting at T=0.05) is confirmed essential. All solutions here use it.

---

## What Did NOT Work

- **Step function init**: Consistently worst performer (1.519-1.522). The discontinuities don't survive optimization well.
- **Comb init**: Middling (1.515-1.518). Better than step but worse than arcsine.
- **3-stage pipeline**: Not a consistent improvement. Adds ~50% more compute for ~0 gain.
- **Gaussian inits**: Failed to rank in coarse top-5 when competing against arcsine (sol04). Consistent with prior generation findings — Gaussian inits converge to the same ~1.509 basin.

---

## Key Hypotheses

1. **Arcsine inits find a similar basin to Gaussian inits, not a new one.** The scores are very close (1.508974 vs 1.5091). The arcsine may give marginal advantage due to its bimodal U-shape providing better initial asymmetry, but the final basin appears to be the same.

2. **Basin floor near 1.509–1.510 for coarse-to-fine + warm smooth-max.** All 4 solutions cluster in 1.509–1.511. Something qualitatively different is needed to break below 1.505.

3. **Noise-key sensitivity is high.** The same arcsine config with different noise keys gives results ranging from 1.508974 to 1.553228. Many of the "arcsine" improvements may just be lucky noise realizations, not structural advantages.

---

## What I Lacked / Would Do Differently

1. **Actual simulated annealing at coarse scale** (Boyer et al. approach) was not implemented. This was the #1 priority in the State of Affairs and could find genuinely different basins.

2. **Warm-start polish from sol01 result**: Loading the C=1.508974 solution and running extended fine annealing (to T=0.0001 or T=0.00003) was not tested — would be cheap and potentially effective.

3. **More seeds of the exact winning config from sol01**: The sol01 winner used a specific noise key from `hash('arcsine') % 97`. With 20+ seeds of the same (a,b,tilt), we might find even better noise realizations.

4. **Extended temperature schedule**: Adding T=0.0001 or T=0.00003 phases after T=0.0003 was not tested for arcsine inits specifically (State of Affairs reported this as negligible for Gaussian, but untested for arcsine).

---

## Specific Experiments to Run Next

1. **SA at coarse scale (N=80, 5000 SA steps) → upsample → warm fine**: Implement Metropolis SA using smooth_c at T=0.05 as the energy. Expected to find qualitatively different basins.

2. **Warm-start polish**: Re-run sol01 to get the 1.508974 array, then apply fine annealing from T=0.05→T=0.0001 (6 phases × 20k steps) as a polishing step.

3. **Controlled noise-seed scan**: Fix the winning arcsine config (a=-0.05, b=0.22, tilt=0.1→0.5) and run 50+ seeds to map the distribution of achievable C values. Understand whether 1.5090 is reproducible or a lucky outlier.

4. **Arcsine + Gaussian composite**: Init as weighted sum of arcsine U-shape and a single narrow Gaussian, to get a 3-peak structure (arcsine peaks + Gaussian peak at a custom location).

---

## Surprising Findings

- The arcsine initialization finding was genuinely surprising: U-shaped init (high at interval edges, low in center) performs better than bell-shaped Gaussian init. This suggests the optimal function may have a bimodal structure — consistent with the mathematical form of solutions to related variational problems.
- In sol04, ALL top-5 coarse solutions were arcsine; Gaussians failed to rank. This is stronger evidence than I expected that arcsine is finding a structurally different (or at least higher-quality) coarse basin.
- The mirror-image configurations (a=-0.22, b=0.05 with negative tilt) consistently perform nearly as well as the original (a=-0.05, b=0.22 with positive tilt), suggesting the problem has approximate reflection symmetry at this resolution that the fine-stage optimization breaks.
