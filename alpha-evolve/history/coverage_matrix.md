# Coverage Matrix — Generation 2

**Sparse format: only tested combinations shown. Cap: top 15 ideas by usage.**
**Lower score is better (minimize C).**

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|---|---|---|---|---|
| idea_001 (Adam) alone | 1 | 1.5182 | 1.5182 | gen_1 |
| idea_001 + idea_007 (smooth-max) + idea_008 (multi-seed) | 2 | 1.5108 | 1.5130 | gen_1 |
| idea_001 + idea_007 + idea_008 + idea_004 (coarse-to-fine, **warm** fine) | 2 | **1.5091** | 1.5092 | **gen_2** |
| idea_001 + idea_007 + idea_008 + idea_004 (coarse-to-fine, **cold** fine) | 1 | 1.5188 | 1.5188 | gen_2 |
| idea_001 + idea_007 + idea_008 + idea_010 (L-BFGS polish) | 2 | 1.5107 | 1.5108 | gen_2 |
| idea_001 + idea_007 + idea_008 + SA-fine-grid | 3 | 1.5108 | 1.5149 | gen_2 |
| idea_001 + idea_008 + idea_010 (L-BFGS) | 2 | 1.5155 | 1.5156 | gen_1 |
| idea_001 + idea_008 + idea_012 (asymmetric) | 1 | 1.5249 | 1.5249 | gen_1 |
| idea_001 + idea_011 (Lion) + idea_008 | 1 | 1.5182 | 1.5182 | gen_1 |
| idea_001 + idea_011 (Lion) + idea_002 (N=1000) | 1 | 1.5207 | 1.5207 | gen_1 |
| idea_001 + idea_003 (shape prior) + idea_002 (N=800) | 1 | 1.5207 | 1.5207 | gen_1 |
| idea_001 + idea_004 (multi-scale, cold, no smooth-max) | 2 | 1.5270 | 1.5500 | gen_1 |
| idea_001 + idea_010 (L-BFGS) alone | 1 | 1.5189 | 1.5189 | gen_1 |
| idea_001 + idea_008 + idea_002 (N=1500) | 1 | 1.5183 | 1.5183 | gen_1 |
| idea_006 (Fourier basis) + idea_001 | 1 | 1.5294 | 1.5294 | gen_1 |
| idea_003 (Gaussian mixture) + idea_001 | 1 | 1.5801 | 1.5801 | gen_1 |
| idea_010 (L-BFGS only, no Adam) | 1 | 1.6887 | 1.6887 | gen_1 |
| idea_006 (analytical only, no optim) | 1 | 3.0000 | 3.0000 | gen_1 |

## Unexplored High-Priority Combinations for Gen 3

1. **SA at coarse scale (N=30–80) + upsample + smooth-max fine** — Boyer et al.'s actual approach. Not yet tried.
2. **Warm-start from 1.5091 solution + extended fine annealing** — Fast experiment, high upside.
3. **idea_007 + idea_011 (Lion warmup) + idea_004** — Lion for coarse exploration combined with coarse-to-fine.
4. **idea_006 (Fourier basis) + idea_007 (smooth-max)** — Fourier without smooth-max was 1.5294; combination unexplored.
5. **Non-Gaussian coarse initializations** (comb, step, arcsine) + coarse-to-fine + smooth-max.

## Confirmed Dead Ends

- SA at N=600 (fine-grid): returns to same basin every time
- L-BFGS after smooth-max convergence: zero effect
- More restarts (>8) or more steps (>15k/phase) with standard approach: diminishing returns
- Cold fine stage in coarse-to-fine: 1.5188 (no improvement)
