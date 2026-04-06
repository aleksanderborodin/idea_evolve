# Observations — explore_2, Generation 1

## Problem
Find the largest Sidon set in {0, ..., 10000}. Baseline greedy: 66. Target: 100.

## Key Findings

### Greedy baseline is a strict local optimum under many perturbations

- Sequential greedy (0,1,2,...,N) always gives **66** elements, regardless of ordering.
- Random-order greedy gives **62** on average (max 62 in 10 trials) — WORSE than sequential.
- Greedy from the union of 10 different random sets still gives **66**.
- Exhaustive single-removal + sequential greedy refill: **NO improvement** from the 66-element greedy set.
- This means the greedy 66-element set is a strict local optimum under 1-opt.

### 2-opt can escape: remove 2 elements, add 3+ genuinely new ones
- sol04 found **67** using random pair sampling with 3 genuinely new elements added (net gain 1).
- sol05 found **66** using "exhaustive" 2-opt, but had a bug: greedy re-adds the removed elements (net gain 0).
- sol06 tried to fix this but introduced a violation (fitness 0).

### Simulated annealing baseline: modest gains
- sol01 (SA with swap+add+perturbation moves, 27s): **68** — best result.
- The SA works by slowly reorganizing the set; 27 seconds gives modest improvement.

## Solutions Tried

| File   | Approach                                     | Fitness | Valid |
|--------|----------------------------------------------|---------|-------|
| sol01  | Simulated annealing (swap, add, perturb)     | 68      | yes   |
| sol02  | ILS with blocking score + random perturbation| 0       | no    |
| sol03  | Numpy-vectorized ILS                         | 66      | yes   |
| sol04  | Targeted removal + exhaustive 2-opt (random) | 67      | yes   |
| sol05  | Exhaustive 2-opt (bug: re-adds removed)      | 66      | yes   |
| sol06  | Fixed 2-opt (new bug: creates violation)     | 0       | no    |

**Best valid solution: sol01 with fitness 68.**

## What Went Wrong

1. **sol02**: The blocking score computation was O(|S|^2) per iteration, making it too slow and/or the implementation had a subtle validity bug.
2. **sol05**: The 2-opt greedy greedily re-adds the removed elements in sequential order, giving net gain 0. The exhaustive search was correct, but found no improvements because greedy undid the removal.
3. **sol06**: Tried to fix sol05 by excluding removed elements, but introduced a different bug causing a 1-violation invalid set.

## What I Didn't Know / Wished I Had

- Known best Sidon set sizes for N=10000 (literature values would help set realistic targets).
- Whether algebraic constructions (Singer sets for q≈99) beat 68 — the other agent is handling this.
- Fast C implementation or numpy solution for is_sidon (pure Python SA is slow).

## What I Would Do Differently

1. **Fix the 2-opt bug properly**: the key insight is correct — need to exclude removed elements from the addable set, then greedily fill, then optionally re-add removed elements.
2. **Run iterative 2-opt**: if each 2-opt pass improves by 1, iterate until no improvement.
3. **Larger SA neighborhoods**: remove 15-25 elements (not 2-8), greedy refill with multiple random orderings, SA acceptance.
4. **Better SA cooling**: the 27s SA (sol01) reached 68 but barely exceeded baseline. Slower cooling or reheating might help.

## Hypotheses for Future Agents

1. **The 66→67 2-opt transition exists**: sol04 found it. A fixed exhaustive 2-opt from the 67-element set might find a 68→69 transition, and so on iteratively.
2. **Temperature-adaptive SA**: if we keep temperature high for longer (accept moves that decrease size by 3-5), we might reach qualitatively different regions of the search space.
3. **Large random perturbations + sequential greedy**: removing 20-30 elements and greedy-refilling always gives back ~66. But with DIFFERENT greedy orderings (not random, but structured), we might find 70+.
4. **Algebraic constructions** (other agent): Singer set for q=97 gives 98 elements in {0..9506} ⊂ {0..10000}. This would be a massive jump.
