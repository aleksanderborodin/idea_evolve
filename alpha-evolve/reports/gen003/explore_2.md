# Debrief Report — gen003_explore_2

**Agent:** explore_2, generation 3
**Directive:** Test structurally diverse coarse initializations with coarse-to-fine + warm smooth-max. Compare Gaussian, comb, step, and arcsine-weighted init families.

---

## Solution Table

| File   | Fitness (C) | is_valid | Approach |
|--------|-------------|----------|----------|
| sol01  | **1.508974** | 1 | 3 families × 2 seeds each (arcsine won) |
| sol02  | 1.510186    | 1 | Arcsine deep-dive: 10 subinterval configs |
| sol03  | 1.509114    | 1 | Arcsine 3-stage N=80→200→600, 12 seeds |
| sol04  | 1.509226    | 1 | 25-seed coarse funnel → top-5 fine |

**Prior best:** C = 1.5091 (gen002_explore_1_sol03)
**This session best:** C = 1.508974 (sol01) — marginal improvement

---

## What I Tried

### 1. sol01 — Init family comparison
Three init families (comb, step, arcsine) × 2 seeds each at N=80. Coarse-to-fine with warm fine stage. Arcsine on subinterval [-0.05, 0.22] with positive tilt won decisively.

### 2. sol02 — Arcsine subinterval sweep
10 configurations varying (a, b, tilt) for the arcsine init. Confirmed that positive-biased [−0.05, 0.22] and mirror [−0.22, 0.05] are the best subintervals. Score variance is high due to noise-key sensitivity.

### 3. sol03 — 3-stage pipeline on arcsine
Added intermediate N=200 optimization stage. 12 seeds across the (a, b) space near the sol01 winner. The extra stage added compute without consistent benefit. Best C=1.509114, slightly worse than sol01.

### 4. sol04 — 25-seed coarse funnel
Ran 25 diverse short coarse runs (12 arcsine + 8 Gaussian + 5 comb). Selected top-5 by coarse C. Ran full warm fine on top-5. ALL top-5 coarse candidates were arcsine-initialized. Best C=1.509226.

---

## Key Findings

1. **Arcsine initialization is superior to Gaussian, comb, and step at coarse scale.** When 25 diverse seeds compete, arcsine family occupies all top-5 coarse slots. The U-shaped profile (peaks at interval endpoints) consistently outperforms round bell-shaped initializations.

2. **Hypothesis partially confirmed:** Arcsine inits may find a marginally different basin (1.5090 vs 1.5091), but the improvement is small. The families may converge to the same ~1.509 attractor.

3. **Subinterval placement matters:** Subintervals biased toward one half of the domain (either positive or negative) work better than centered or full-domain arcsine.

4. **3-stage pipeline (N=80→200→600) does not improve over 2-stage (N=80→600)** for this problem.

5. **Step function init is a dead end.** Always in 1.519–1.522 range. Do not revisit.

---

## What Information I Lacked

- The exact noise key used in sol01's winning run (Python `hash()` is non-deterministic), making it hard to replicate the 1.508974 result precisely.
- Whether the 1.508974 result is reproducible or a lucky outlier (would need 50+ seeds of same config to assess).
- Coarse-scale SA (Boyer et al.) was not implemented — this remains the most promising untested approach per State of Affairs.

---

## State of Affairs Accuracy

The State of Affairs was accurate. It correctly identified:
- Arcsine/non-Gaussian coarse inits as high-priority untested direction
- Coarse-scale SA as #1 priority (still untested)
- Warm fine stage as essential (confirmed again)

Missing from State of Affairs: the observation that arcsine inits dominate Gaussian even at coarse scale (not just fine scale).

---

## Recommended Next Experiments

1. **Priority 1 — Coarse-scale SA at N=80**: Implement Metropolis SA using smooth_c as energy. This is Boyer et al.'s actual approach and the only major unexplored direction. Expected to find qualitatively new basins.

2. **Priority 2 — Warm-start polish on sol01 result**: Load C=1.508974 solution, run extended fine annealing [0.05, 0.01, 0.003, 0.001, 0.0003, 0.0001, 0.00003] with 20k steps each.

3. **Priority 3 — Arcsine noise-seed scan**: Fix (a=-0.05, b=0.22, tilt=0.1→0.5) and run 50 noise seeds to map C distribution. Understand whether 1.5090 is the best achievable or whether lucky seeds can find 1.505.

4. **Priority 4 — Arcsine + Gaussian composite**: Init as arcsine U-shape + narrow Gaussian at a custom position = 3-peak structure. May find basins inaccessible to either pure arcsine or pure Gaussian.

---

## What Would I Do Differently

- Start directly with the 25-seed funnel approach (sol04 structure) rather than building up through sol01→sol02→sol03.
- Implement SA at coarse scale as one of the initial experiments — the State of Affairs marked this as #1 priority.
- Save intermediate optimized arrays to disk so warm-start polish can be done without full re-optimization.
