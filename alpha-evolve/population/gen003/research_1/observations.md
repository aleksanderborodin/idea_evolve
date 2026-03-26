# Observations — Research Agent gen003_research_1

## Summary

Primary objective was to find and retrieve the AlphaEvolve solution array for the First Autocorrelation Inequality.

**Result: SUCCESS.** The exact 1319-element array was retrieved from:
`github.com/google-deepmind/alphaevolve_repository_of_problems`
Cell 60 of `experiments/autocorrelation_problems/autocorrelation_problems.ipynb`

## Solution Retrieved

- **sol01.py**: AlphaEvolve array (1319 elements), C = **1.5031635546815612**
  - Source: Georgiev-Gómez-Serrano-Tao-Wagner, Dec 2025
  - Improvement over our gen002 best (1.5091): **−0.0059**
  - Improvement over baseline (1.5185): **−0.0153**
  - This is **below our target of 1.5053** — target is met.

## Key Findings During Research

1. **Best known bound updated**: The AlphaEvolve repository shows C ≤ 1.5029 by Yuksekgonul et al. (Jan 2026), even better than the 1.5032 we retrieved.

2. **Multiple intermediate arrays available** in the notebook:
   - Cell 46 (score 1.5053): 600-element array — the original AlphaEvolve result
   - Cell 49 (score 1.5040): ~1136 elements
   - Cell 52 (score 1.5036): ~891 elements
   - Cell 54 (score 1.5035): ~1022 elements
   - Cell 56 (score 1.5035): ~1417 elements
   - Cell 58 (score 1.5033): ~3530 elements
   - Cell 60 (score 1.5032): 1319 elements ← retrieved
   - Cell 91: ~50000 elements (very sparse comb, likely ThetaEvolve/different problem)

3. **Evaluation formula confirmed equivalent**: The notebook uses `2*n*max_b/sum_a^2`; our evaluator uses FFT-based compute_c. Both give 1.503164 for this array.

4. **AlphaEvolve's search algorithm**: Hybrid memetic algorithm combining:
   - LP-guided gradient direction (solve_convolution_lp)
   - Cubic backtracking line search with momentum
   - Simulated annealing perturbations with sine-map pseudo-random
   - Temperature cooling tied to remaining runtime

5. **The 1319-element array structure**: Dense non-zero region in first ~25 elements (0.4–0.7 range), large sparse gap of near-zeros (~indices 25–120), then complex multi-peaked structure from ~120–1319. This is qualitatively different from our gradient-descent solutions.
