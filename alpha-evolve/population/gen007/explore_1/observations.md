# Observations — explore_1, Generation 7

## Summary

Triplet perturbation (integral-preserving 3-element moves) finds genuine improvements
on the TTT-Discover 30k solution, disproving pair-optimality.

## Approaches Tried

### Triplet Perturbation (GRADIENT-GUIDED, SUCCESS)
- **Method:** For each triplet (i, j, k), compute the first-order gradient of the
  autoconv maximum w.r.t. (d1, d2) under the integral-preservation constraint d1+d2+d3=0.
  Gradient: alpha = f[(n*-i)%M] - f[(n*-k)%M], beta = f[(n*-j)%M] - f[(n*-k)%M].
  Move in the direction (-alpha, -beta) / ||(alpha, beta)||.
- **60,000 trials** with 4 strategies: random nonzero, large+small+random, neighbor triplets,
  fully random. Step sizes tried per trial: [1e-7, 5e-7, 1e-6, 5e-6, 1e-5, 5e-5, 1e-4, 5e-4, 1e-3].
- **Result: 160 improvements**, C improved from 1.5028628724712894 → 1.5028628688924555 (delta: -3.578e-9)
- Speed: ~220 trials/second via incremental autoconv updates (O(N) per update, no FFT per trial)

### Second Pass — After first 60k trials (ZERO improvements)
- 20k additional random/structured triplets
- 0 improvements found
- Suggests triplet optimum largely reached after 60k trials, or diminishing returns

## Key Findings

1. **Triplet moves find improvements where pairs cannot.** Pair-wise perturbation found only
   1 improvement in 300 trials (gen 6). Triplet moves found 160 in 60k trials. Different
   perturbation structure — coordinated 3-element moves access improvement directions
   inaccessible to pairs.

2. **Improvement rate decays quickly.** First 20k trials: ~100 improvements. Last 20k trials:
   ~20 improvements. The triplet-reachable improvements are concentrated at the start.

3. **The ~6.3% zero-gradient triplets.** 6331/60000 triplets had alpha≈0 AND beta≈0, meaning
   the first-order gradient at n* was zero for that triplet. These were skipped. This fraction
   grows over time as the solution becomes more uniform near n*.

4. **Delta of -3.578e-9** vs coordinate descent's -2.58e-8 over 14k improvements in gen 6.
   Triplets are less effective per trial than single-element moves, but they proved the
   solution is NOT at the triplet optimum.

5. **Proof of triplet non-optimality.** The fact that 160 improvements were found proves
   definitively that the current solution is not triplet-optimal. The solution has headroom
   under 3-element coordinated moves.

## Hypotheses for Unexplored Directions

1. **Combined coordinate descent + triplet interleaving:** The solution is still not
   coordinate-wise optimal (gen 6 showed 1800 improvements/round). Run extended coordinate
   descent, then triplet, then coordinate descent again in alternating rounds.

2. **Quadruplet moves:** If triplets add to pairs, do quadruplets add to triplets? With
   N=30k, each quadruplet search is more expensive but might find further improvements.

3. **Larger step sizes for triplets:** The improvements found were at small deltas (1e-6
   to 1e-4 range). Larger coordinated moves (e.g., 0.01-scale) might escape the local
   minimum entirely by shifting mass more aggressively.

4. **Momentum-enhanced triplets:** Instead of random triplets, use the gradient from
   accepted improvements to guide next triplet selection. Accept improvement → find
   similar triplet nearby → continue moving in the same direction.
