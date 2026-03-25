# Observations — gen001 explore_1

## Summary

Tried 7 solutions (sol01–sol07) focused on advanced numerical optimization with shape priors and multi-scale refinement. Baseline: 1.5185 at N=600, 40k Adam steps.

## Results

| Solution | Fitness  | Approach |
|----------|----------|----------|
| sol01    | 1.5207   | Gaussian init (σ=0.08), N=800, 100k Adam steps |
| sol02    | 1.5270   | Multi-scale: Hann init N=200→600→1200, 25k+30k+25k steps |
| sol03    | 1.5189   | Baseline init + 30k Adam + L-BFGS-B fine-tune |
| sol04    | 1.5182   | Baseline init + 80k Adam (2× longer baseline) |
| sol05    | **1.5155** | 8 seeds × 15k Adam (shifted support), best → 60k Adam + L-BFGS |
| sol06    | 1.5183   | 16 seeds × 10k Adam, top-3 → 60k Adam, upsample N=1500 + L-BFGS |
| sol07    | unknown  | 32 seeds (16 diverse modes × 2) × 12k Adam, top-3 → 100k Adam + L-BFGS |

## What Worked

- **Multiple random seeds with shifted initialization support** (sol05: 1.5155) was the clear winner, beating the baseline by ~0.003.
- More steps with baseline init (sol04: 1.5182) gives marginal improvement over baseline.
- L-BFGS alone on top of Adam (sol03) gave negligible improvement.

## What Didn't Work

- **Gaussian initialization** (sol01): Symmetric shape starts in a worse basin; ends up at 1.5207 worse than baseline despite 100k steps and N=800. Symmetric initializations are likely poor for this problem since C ≥ 2 for symmetric functions.
- **Multi-scale N=200→1200** (sol02): Hann window init + coarse-to-fine gave 1.5270, worst of all. The coarse optimization converged to a bad local minimum that persisted at finer scales.
- **Upsampling to N=1500** (sol06): Upsampling the best N=600 solution to N=1500 and running only 20k more steps was insufficient; the high-res function needs many more steps to re-converge. Result was 1.5183, worse than sol05.

## Key Insight Discovered

The optimal function for this problem is likely ASYMMETRIC. For symmetric (even) functions, C ≥ 2 analytically (by Cauchy-Schwarz on the autoconvolution). The baseline achieves C ≈ 1.52 < 2 because gradient descent breaks the initial symmetry. Deliberately exploring asymmetric initializations (shifted support blocks) leads to finding better basins (sol05 1.5155).

## Hypotheses for Future Exploration

1. **Even more seeds with asymmetric init**: sol07 (32 seeds, 16 asymmetric modes) should help; wasn't fully evaluated.
2. **Offset blocks at specific positions**: Shift the support block to [N//2, N] or [N//3, N] explicitly, which forces asymmetry from the start.
3. **Higher resolution with adequate steps**: N=1200 with 100k+ steps might yield better results than N=600.
4. **Simulated annealing / noise injection**: Add periodic perturbation noise to escape local minima during Adam.
5. **Right-biased initialization**: Support near x=1/4 (right boundary) may be the right basin.

## Information Lacking

- What shape does the optimized function actually take? Need to visualize the N=600 optimized function from sol05 to understand the shape.
- Are there published results on the exact function shape for this extremal problem?
- What is the theoretical lower bound derivation for C ≥ 1.28 and what function achieves it?

## Surprising Results

- Gaussian init (sol01) was WORSE than baseline despite more steps and higher N. Symmetry kills it.
- Multi-scale was the worst approach despite being theoretically sound. The Hann window initialization led to a bad basin.
- Multi-seed is surprisingly effective — just varying the support position by small offsets reveals significantly different function families.
