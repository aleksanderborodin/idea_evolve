# Observations — gen003_explore_1

## Summary of attempts

All three solutions implemented coarse-scale Simulated Annealing (SA) as directed by the brief (Boyer et al. approach). None beat the current best of C=1.5091.

---

## sol01 — N=40 coarse SA, 4 seeds × 25 SA iters × 5k inner steps

- **Score: C = 1.5148**
- SA acceptance rate: 96-100% throughout all seeds — SA temperature far too high relative to coarse C differences
- sigma: based on 0.3 * mean(|f|) which was correctly scaled initially, but N=40 coarse gave poor upsampling
- Problem: N=40 gives insufficient resolution for meaningful upsampling to N=600; fine-tuning couldn't recover
- Coarse best: C ≈ 1.527 (N=40). After fine-tuning: 1.5148

## sol02 — N=80 coarse SA, 3 seeds × 30 SA iters × 24k inner steps

- **Score: C = 1.5155**
- Sigma fixed to: 0.4 * std(raw_params) — WRONG: std(raw_params) grew to 15-25, giving huge perturbations that randomized the solution
- Acceptance rate: started at 100%, decayed to 50-63% by end (because metro temp decayed, but sigma grew)
- SA didn't explore meaningfully different basins at coarse level
- Coarse best: C ≈ 1.520 (N=80). After fine-tuning: 1.5155
- Worse than baseline (1.5093) despite using N=80 — only 3 seeds vs baseline's 8 seeds

## sol03 — N=30 coarse SA, 4 seeds × 35 SA iters × 15k inner steps

- **Score: C = 1.5169**
- Sigma: 0.35 * mean(softplus(raw)) — but mean(f) was large (20-40) making sigma=7-15
- Acceptance rate: 54-89% — still too permissive
- At N=30, coarse C was ~1.53-1.54, giving fine C ~1.52
- Worse than sol01 and sol02

---

## Why SA didn't work as expected

1. **Metropolis temperature calibration failure**: In all runs, acceptance rates were 60-100%. The SA was accepting nearly everything and not being selective. The Metropolis temperature needs to be tuned to the scale of the energy landscape, and the coarse C differences (~0.001-0.005) require metro_temp ≈ 0.0005-0.001 to get 20-40% acceptance — much smaller than the 0.003-0.008 used.

2. **SA not finding better basins**: All seeds converged to coarse C ≈ 1.52-1.54 regardless of SA. The coarse landscape seems to have a wide basin of attraction that all initializations fall into. SA with these parameters didn't escape it.

3. **Fine-tuning quality**: The baseline (gen002 sol02: 8 seeds, no SA) achieves 1.5093. My SA runs used only 3-4 seeds for the fine-tuning stage. Even without SA, 4-8 diverse seeds with the standard coarse→fine approach would likely get 1.510-1.511.

4. **Key insight missed**: Boyer et al. ran SA at N=23 — significantly coarser than N=30-80. At N=23 there are only 23 degrees of freedom; the SA can hop between fundamentally different solutions. At N=30-80, the landscape is still complex and SA with 35 iterations isn't sufficient.

---

## What would have helped

- Run the fine-tuning on ALL seeds independently (not just global best coarse), then take best final result — this alone would match the gen002 baseline
- Use much smaller Metropolis temperature (metro_temp_0 = 0.0005-0.001) to get selective acceptance
- More SA iterations (100+) with shorter inner steps (1k-2k)
- Try N=23 as Boyer et al. actually used
- OR: skip SA entirely and run 8-12 diverse seeds with 3-stage coarse→fine (proven to get 1.5091)
- OR: warm-start from the AlphaEvolve solution (C=1.5032) and run gradient polishing

---

## Unexplored directions from this session

1. Warm-start from AlphaEvolve array (C=1.5032) + warm smooth-max fine-tuning — highest value, possibly pushes below 1.503
2. SA at N=23 (exact Boyer et al. scale) with much lower Metropolis temperature
3. Run 8-12 seeds coarse→fine→fine (3-stage N=80→200→600) — gen002 sol03 showed promise but timed out
