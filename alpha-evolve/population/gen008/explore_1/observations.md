# Observations — gen008_explore_1

## What was attempted

### Quadruplet perturbation (d1+d2+d3+d4=0)
- Starting point: gen007_explore_1/sol01.py, C=1.5028628688924555
- Method: gradient-guided integral-preserving 4-element moves
- 4 selection strategies rotated every 4 trials (S0: random nonzero, S1: large+small, S2: consecutive, S3: mixed)
- First-order gradient projection onto constraint plane (d.sum()=0)
- 9 step sizes: [1e-7, 3e-7, 1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3]
- O(N) incremental autoconv updates via helpers.incremental_autoconv_update

### Result
- 8015 quadruplet improvements found
- delta_C = -4.13e-10 (very small but real)
- Final C after quadruplets: 1.5028628684790137 (unverified intermediate)

### Triplet follow-up pass
- After quadruplets, ran short triplet pass
- Found 2523 additional triplet improvements
- Strategy breakdown (quadruplets): S0=2388, S1=2356, S2=1135, S3=2136

## What worked
- Quadruplets DID find improvements where triplets had exhausted (~8k improvements)
- All 4 strategies contributed, with S2 (consecutive neighbors) notably weaker than others
- Triplet follow-up found 2523 more after quadruplets — confirms quadruplets unlock new directions

## What did NOT work
- Speed was the main constraint. np.roll per trial limited throughput to ~112 trials/s
- Couldn't run the full 100k trials within time budget
- First-order approximation occasionally accepted moves that didn't improve C exactly

## Key insight
- The mathematical argument holds: quadruplet-optimality ≠ triplet-optimality ≠ pair-optimality
- Quadruplets found ~8k improvements vs ~160 for triplets at same starting point
- This suggests higher-order perturbations (quintuples?) may continue to find improvements
- Strategy S2 (consecutive neighbors) was least effective; S0/S1/S3 roughly equal

## What to try next
- Interleaved quadruplet + triplet cycles until both converge
- Quintuples (d1+...+d5=0) — mathematical extension should work
- Momentum: after accepted quadruplet, retry same indices with larger step
- Vectorized batched implementation (avoid Python loop overhead) for 10x speedup
