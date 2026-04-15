# Observations — explore_2, Generation 1

## What I Tried

### ILNS v1 (sol01.py) — 290 codewords
- Iterated Large Neighborhood Search with 8 restarts × 300 iterations
- Destroy fraction: 20-40% randomly
- Result: 290 codewords (beats greedy baseline of 262)

### Aggressive ILNS v2 (sol02.py) — 284 codewords
- 20 restarts × 600 iterations, larger destroy fractions (30-50%)
- Result: 284 (slightly worse than v1, more iterations didn't help)

### Genetic Algorithm (sol03.py) — ERROR
- Population of 40, crossover + mutation
- Crashed due to empty array dtype bug (fixed but too slow to evaluate)

### ILNS v5 (sol05.py) — 293 codewords
- 15 restarts × 400 iterations
- Best result achieved: 293 codewords
- ILNS helps vs pure greedy but diminishing returns

## Key Findings

1. **Greedy alone caps at ~250-260** from random starting points
2. **ILNS improves to ~290-293** - about 15% improvement over greedy
3. **Still far from 616** (AGL-based construction) - non-algebraic approaches lag significantly
4. **Without group structure, search space is vast** - ILNS/GA struggle to explore effectively

## Why ILNS/GA Struggle

The bucket structure (70 buckets for d=5, n=8) means:
- Each codeword eliminates ~8-10% of remaining perms
- The greedy heuristic is actually quite good locally
- Destroy-repair breaks up good local structure without finding better global optima
- The problem is NP-hard and ILNS doesn't have the right bias

## What Would Help

1. **Better neighborhoods** - current destroy-repair is too coarse
2. **Smarter perturbation** - remove codewords that "block" many others, not random
3. **Guided restart** - start from codewords that belong to underexplored bucket regions
4. **Hybrid with algebraic hints** - even without full AGL structure, some orbit awareness helps