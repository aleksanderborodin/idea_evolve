---
type: idea
id: idea_013
name: "Variable Neighborhood Search (VNS)"
lifecycle: active
confidence: 0.5
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: null
supported_by: []
contradicted_by: []
related_ideas: [idea_006, idea_004]
cluster: cluster_002
tags: [VNS, local-search, systematic-neighborhoods, unexplored]
---

# Variable Neighborhood Search (VNS)

## What It Is

A systematic neighborhood search that varies the destruction/repair structure across predefined neighborhoods: small removal (1-2 codewords), medium removal (5-10%), large removal (20-30%), very large removal (50%). VNS systematically shakes the solution across different scales rather than random destroy fractions.

## How It Would Work

1. Define neighborhoods: k ∈ {1, 2, 5, 10, 20, 50} (percentage of codewords to remove)
2. For each neighborhood k:
   a. Remove k% of codewords from current solution
   b. Greedily rebuild
   c. If improvement, move to new solution and reset k=1
   d. Else, try next k
3. Continue until max iterations or convergence

## Evidence

- **Not yet implemented** in any generation 1 solution
- Proposed by research_1 as a better alternative to random-destroy ILNS
- ILNS with random destroy fractions (20-50%) achieved 290-293
- VNS's systematic approach may find neighborhoods that random destroy misses

## Current Status

**Unexplored**. Recommended by research_1 but not yet tried.

## Expected Performance

Likely better than ILNS with random destroy fractions, but still limited by lack of algebraic structure. Expected ~300-350 if well-implemented (speculative).

## Why It Matters

Random destroy in ILNS may systematically miss certain neighborhood structures. VNS's deterministic neighborhood ordering ensures coverage of all scales.
