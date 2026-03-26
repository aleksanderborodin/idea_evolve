# Coverage Matrix — Generation 4

**Sparse format: only tested combinations shown. Cap: top 20 ideas by usage.**
**Lower score is better (minimize C).**

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|---|---|---|---|---|
| idea_014 + idea_018 (TTT-Discover verbatim) | 1 | **1.5029** | 1.5029 | **gen_4** |
| idea_014 (AlphaEvolve verbatim) | 1 | 1.5032 | 1.5032 | gen_3 |
| idea_014 + idea_007 + idea_009 (warm-start polish, conservative) | 1 | 1.5032 | 1.5032 | **gen_4** |
| idea_001 + idea_007 + idea_008 + idea_004 (warm fine) + idea_013 (arcsine) | 3 | 1.5090 | 1.5095 | gen_3 |
| idea_001 + idea_007 + idea_008 + idea_004 (warm fine) | 2 | 1.5091 | 1.5092 | gen_2 |
| idea_001 + idea_007 + idea_004 + idea_015 (DCT perturb) | 1 | 1.5091 | 1.5091 | gen_3 |
| idea_001 + idea_007 + idea_008 + idea_004 (3-stage) + idea_013 | 1 | 1.5091 | 1.5091 | gen_3 |
| idea_001 + idea_007 + idea_008 (25-seed funnel) + idea_004 + idea_013 | 1 | 1.5092 | 1.5092 | gen_3 |
| idea_001 + idea_007 + idea_004 + extended polish (T=0.00003) | 1 | 1.5093 | 1.5093 | gen_3 |
| idea_001 + idea_007 + idea_008 + idea_013 (arcsine sweep) + idea_004 | 1 | 1.5102 | 1.5102 | gen_3 |
| idea_001 + idea_007 + idea_008 + idea_010 (L-BFGS polish) | 2 | 1.5107 | 1.5108 | gen_2 |
| idea_001 + idea_007 + idea_008 | 2 | 1.5108 | 1.5130 | gen_1 |
| idea_001 + idea_007 + idea_008 + SA-fine-grid | 3 | 1.5108 | 1.5149 | gen_2 |
| idea_001 + idea_007 + idea_004 + coarse-SA (N=40) | 1 | 1.5148 | 1.5148 | gen_3 |
| idea_001 + idea_007 + idea_004 + coarse-SA (N=80) | 1 | 1.5155 | 1.5155 | gen_3 |
| idea_014 + idea_002 (upsample N=2000) + idea_007 | 1 | 1.5159 | 1.5159 | **gen_4** |
| idea_001 + idea_007 + idea_004 + coarse-SA (N=30) | 1 | 1.5169 | 1.5169 | gen_3 |
| idea_001 + idea_008 + idea_010 (L-BFGS) | 2 | 1.5155 | 1.5156 | gen_1 |
| idea_001 (Adam) alone | 1 | 1.5182 | 1.5182 | gen_1 |
| idea_001 + idea_011 (Lion) + idea_008 | 1 | 1.5182 | 1.5182 | gen_1 |
| idea_001 + idea_004 + idea_007 (cold fine) | 1 | 1.5188 | 1.5188 | gen_2 |
| idea_014 + idea_007 + idea_009 (warm-start aggressive, sigma=0.1) | 1 | 1.5242 | 1.5242 | **gen_4** |
| idea_001 + idea_003 (shape prior) + idea_002 (N=800) | 1 | 1.5207 | 1.5207 | gen_1 |
| idea_001 + idea_004 (multi-scale, cold, no smooth-max) | 2 | 1.5270 | 1.5500 | gen_1 |
| idea_006 (Fourier basis) + idea_001 | 1 | 1.5294 | 1.5294 | gen_1 |
| idea_010 (L-BFGS only, no Adam) | 1 | 1.6887 | 1.6887 | gen_1 |
| idea_006 (analytical only, no optim) | 1 | 3.0000 | 3.0000 | gen_1 |

## Unexplored High-Priority Combinations for Gen 5

1. **idea_017 (projected gradient) on TTT-Discover 30k array** — Optimize f directly with clamp-to-0 projection, bypassing softplus dead zones. Highest priority.
2. **Coordinate descent on TTT-Discover 30k array** — Element-wise perturbation, keep improvements. Simple, avoids all parameterization issues.
3. **Warm-start from TTT-Discover 30k with ultra-gentle lr (1e-6)** — May avoid the landscape distortion seen at lr=0.001.
4. **Calibrated SA at N=23 with reduced budget** — explore_1's approach was correct but computation exceeded timeout. 2 seeds, 100 SA iters should fit.
5. **Retrieve Cell 46-58 intermediate arrays** — N=600 arrays at C=1.5053-1.5033 for warm-start at our pipeline's resolution.

## Confirmed Dead Ends

- SA at N=600 fine-grid: returns to same basin every time
- L-BFGS after smooth-max convergence: zero effect (DEBUNKED, idea_010)
- Extended temp schedule beyond T=0.0003: negligible benefit (0.000025)
- DCT perturbation: all perturbation scales return to 1.509 basin (DEBUNKED, idea_015)
- Cold fine stage in coarse-to-fine: 1.5188 (no improvement)
- Step function init: 1.519-1.522 range
- Coarse-SA with poorly calibrated temperatures: 1.5148-1.5169
- Smooth-max Adam warm-start of published solutions: cannot improve them (pattern_007)
- Cubic spline upsample of sparse solutions: destroys structure (gen 4)
- Aggressive perturbation of published solutions: lands in inferior basins (gen 4)
