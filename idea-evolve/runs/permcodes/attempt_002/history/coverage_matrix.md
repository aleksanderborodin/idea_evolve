# Coverage Matrix — Generation 1

## Top Idea Combinations Tried

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|-----------------|-------------|------------|-----------|------------|
| idea_001 alone (AGL orbit clique) | 6 | 616 | 616 | gen_01 |
| idea_005 alone (direct greedy full space) | 1 | 262 | 262 | gen_01 |
| idea_006 + idea_008 (ILNS + bucket compat) | 3 | 293 | 289 | gen_01 |
| idea_001 + idea_003 (orbit + individual extension) | 2 | 616 | 616 | gen_01 |
| idea_001 + idea_004 (orbit + perturbation) | 1 | 616 | 616 | gen_01 |
| idea_001 + idea_011 (orbit + multi-seed search) | 1 | 616 | 616 | gen_01 |
| idea_006 + idea_009 (ILNS + tabu diversification) | 1 | 284 | 284 | gen_01 |
| idea_010 + idea_008 (GA + bucket compat) | 1 | 0 (INVALID) | N/A | gen_01 |

## Single Ideas (not combined)

| Idea | Times Tried Alone | Best Score | Avg Score | Last Tried |
|------|-------------------|------------|-----------|------------|
| idea_001 (AGL orbit clique) | 6 | 616 | 616 | gen_01 |
| idea_005 (direct greedy full space) | 1 | 262 | 262 | gen_01 |
| idea_006 (ILNS) | 3 | 293 | 289 | gen_01 |

## Unexplored Regions (High Priority for Gen 2)

1. **PGL(2,7) orbit clique** — idea_012 not yet tried. PGL(2,7) has 120 orbits of 336 each (vs AGL's 720 orbits of 56). Different orbit structure may yield larger cliques.
2. **Cross-group clique** — AGL × PGL mixed orbit search. Not tried.
3. **Variable Neighborhood Search (VNS)** — Systematic neighborhood changes instead of random destroy fraction.
4. **Simulated Annealing** — Temperature-based acceptance of worse solutions.
5. **Bucket-coverage greedy** — Maximize bucket diversity rather than just code size.
6. **Individual permutation extension of non-AGL codes** — ILNS codes may have extendable permutations.

## Gap Analysis

- **Algebraic approaches (idea_001)**: 6/6 attempts at 616. Extremely consistent.
- **Stochastic without structure (idea_005, idea_006)**: Best is 293. ~47% of algebraic optimum.
- **Hybrid (orbit + individual extension)**: 2/2 attempts at 616 with 0 extensions found.
- **GA crossover**: 1 attempt, crashed. Not viable as tried.

## Strategic Implication

The entire search space is currently covered by AGL orbit clique and its immediate variants. To beat 616, the system must explore fundamentally different group actions (PGL, PSL) or fundamentally different search paradigms (exact branch-and-bound, LP/IP).
