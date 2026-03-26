# Debrief Report — explore_1, Generation 3

**Agent:** explore_1
**Task:** Implement coarse-scale Simulated Annealing (Boyer et al. approach) — SA at N=30-50, upsample, warm fine-tuning

---

## 1. What did I try?

| Solution | Approach | Score | Notes |
|----------|----------|-------|-------|
| sol01 | N=40 coarse SA, 4 seeds × 25 SA iters × 5k inner | 1.5148 | Acceptance 96-100%; metro_T too high |
| sol02 | N=80 coarse SA, 3 seeds × 30 SA iters × 24k inner | 1.5155 | sigma=std(raw_params) grew to 15-25 (unbounded) |
| sol03 | N=30 coarse SA, 4 seeds × 35 SA iters × 15k inner | 1.5169 | sigma=0.35*mean(f) but f values were large (7-15) |

All three solutions are **worse than the current best (1.5091)** and worse than the simple 8-seed baseline (1.5093).

---

## 2. What information did I lack?

- **Calibration data for Metropolis temperature**: I didn't know the typical magnitude of coarse C differences between neighboring local minima. They turned out to be ~0.001-0.005. With metro_temp_0=0.003-0.008, acceptance was 60-100% — not selective enough.
- **What "coarse C" values the baseline achieves**: The gen002 sol02 (N=80, 8 seeds, no SA) achieves fine C=1.5093. I don't know what its intermediate coarse C values were. If coarse C was already 1.52, my SA wasn't improving on that.
- **Boyer et al. exact methodology**: The brief said N=23 but I tried N=30-80. N=23 might have fundamentally different landscape properties.

---

## 3. What given facts might be wrong or outdated?

- The brief says "sigma = 0.3 * mean(|f|)" — this is in function value space. At N=80 with a well-optimized coarse solution, mean(f) ≈ 20-40 (large absolute values), making sigma = 6-15, which is a huge perturbation. The formula may assume f values are in [0,1], not [0,40].
- The belief that "SA at coarse scale finds better basins than random restarts" is not validated. My data shows SA isn't improving over the coarse starting point in any meaningful way.

---

## 4. Was the State of Affairs accurate?

Yes — it correctly identified SA at coarse scale as untested. The State of Affairs was accurate about the dead end of fine-scale SA. However, it did not mention that the AlphaEvolve solution (C=1.5032) is in `population/best.py` — this would have been the highest-leverage direction (warm-start polish from the known-best solution).

---

## 5. What would I do differently?

1. **Check population/best.py first** — it contains the AlphaEvolve solution at C=1.5032. Warm-starting gradient descent from this would be the highest-ROI experiment.
2. **SA calibration test**: Before running 35 SA iterations, run 5 with different sigma/metro_temp and observe acceptance rate. Tune to 20-40% before committing to full run.
3. **Run fine-tuning on ALL seeds**, not just the global best coarse. This alone might match the gen002 baseline.
4. **Use smaller N**: Try N=23 exactly as Boyer et al., not N=30-80.
5. **Lower sigma**: sigma = 0.05 * mean(f) (not 0.3) for meaningful small perturbations at coarse scale.
6. **Lower metro_temp**: metro_temp_0 = 0.0005 → 0.0001 to get 20-40% acceptance.

---

## 6. Specific experiments to run next

1. **Warm-start from AlphaEvolve (highest priority)**: Load `population/best.py` (C=1.5032, N=1319). Convert to raw_params via inv_softplus. Run warm smooth-max Adam (T=0.05→0.01→0.003→0.001→0.0003, 15k-20k steps each). May push below 1.503.

2. **SA with properly tuned temperatures**: metro_temp_0=0.0005, sigma=0.05*mean(f), N=30, 80+ SA iters with 3k inner steps each. First run 5 calibration iters and measure acceptance rate.

3. **N=23 SA**: Follow Boyer et al. exactly — N=23, 1000 SA iterations, 500 inner steps each, metro_temp calibrated for N=23 landscape.

4. **3-stage coarse→fine with more restarts**: N=80→200→600, 12+ seeds. Sol03 from gen002 explore_1 showed this can reach 1.5091 with 12 seeds but timed out. Run with 8 seeds and simpler fine schedule.

---

## 7. What surprised me?

- **SA acceptance rate remained near 100%** despite decreasing metro_temp: because sigma was growing uncontrollably (std(raw_params) increases as optimization proceeds), the perturbations were always landing far from the current solution, in regions with random high C. The 100% acceptance wasn't because everything was better — it was because the inner optimizer always recovered back to approximately the same local minimum.

- **N=40 is too coarse for fine upsampling**: N=40→600 via linear interpolation produces a piecewise-linear function with coarse "steps" that the fine optimizer can't smooth efficiently. N=80→600 is much better.

- **The AlphaEvolve solution has N=1319** with many near-zero values — a fundamentally different structure (sparse, multi-modal) from the smooth Gaussians our optimization finds. This suggests the gradient-descent approach is finding local optima in a very different part of the function space than Boyer et al.

- **SA inner optimizer with warm restart (T=0.05) defeats the purpose**: The warm inner optimizer re-anneals from T=0.05, which means it effectively does a full warm-to-cold schedule and converges back to the same local minimum as the pre-perturbation solution. A cold inner optimizer (T=0.001 only, 3k steps) would be better for finding the local minimum near the perturbation, enabling meaningful SA basin-hopping.
