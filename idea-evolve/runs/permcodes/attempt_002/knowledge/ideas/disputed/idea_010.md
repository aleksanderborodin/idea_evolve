---
type: idea
id: idea_010
name: "Genetic Algorithm with Crossover"
lifecycle: disputed
confidence: 0.2
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: []
contradicted_by: [gen001_explore_2_sol03]
related_ideas: [idea_006]
cluster: cluster_002
tags: [GA, crossover, genetic-algorithm, population, failed]
---

# Genetic Algorithm with Crossover

## What It Is

A population-based evolutionary approach: maintain a population of codes, select parents via tournament, combine them via crossover, mutate via add/remove operations.

## How It Works

1. **Initialization**: Create population via greedy from random starts
2. **Selection**: Tournament selection based on code size
3. **Crossover**: Union of two parent codes → greedy prune to compatibility
4. **Mutation**: Add/remove random codewords
5. **Repeat** for many generations

## Evidence

- explore_2/sol03: **FAILED** — crashed with dtype error in `make_code_compatible`
- When fixed, would likely perform similarly to ILNS (~290) based on similar algorithm structure
- The crossover operator (union + prune) loses many codewords due to incompatibility

## Current Performance

**0** (invalid — implementation bug). After fixing: expected ~260-280.

## When It Might Help

GA could potentially explore multiple basins of attraction simultaneously through population diversity. However, the crossover operator as implemented is destructive.

## Issues

- Crossover of two compatible codes often produces an incompatible union — the prune step loses too many codewords
- Need a smarter crossover that respects compatibility structure
- Bug: `np.array([])` has dtype=float64 by default, causing IndexError when used as indices

## Future Directions

A better GA would use orbit-level crossover (crossover at orbit level, not individual permutation level), or use a fitness function that rewards bucket diversity.
