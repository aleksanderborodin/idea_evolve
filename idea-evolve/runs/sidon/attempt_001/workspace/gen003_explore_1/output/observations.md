# Observations — gen003_explore_1

## Approaches Tried

### sol01: Probabilistic Alteration Method (fitness: 63)
- **Algorithm**: Sample each element of {0,...,10000} with probability p (~0.013). Iteratively remove the element involved in the most violations until the set is a valid Sidon set. Then greedily extend with shuffled remaining candidates.
- **Grid search**: probabilities [0.010, 0.012, 0.013, 0.015] × 40 seeds each = 160 configs.
- **Result**: fitness=63, valid=1, violations=0. Evaluation took 117s.
- **Why it underperforms**: The alteration phase over-removes — starting from ~130 random elements, many collisions require removing down to ~40-50 elements. Greedy extension from a random sparse core finds ~63. This is WORSE than the deterministic greedy baseline of 66, and far below Singer's 102.
- **Conclusion**: The probabilistic alteration method does not find a better basin than greedy. The random starting core is structurally worse than the greedy order.

### sol02: Min-Blocking Greedy (TIMED OUT — no score)
- **Algorithm**: At each step, pick the valid candidate c that would block the fewest other valid candidates. For each candidate c, compute blocking score = |{c' valid : (c'-c) or (c-c') ∈ new_diffs_from_c}|. Random tie-breaking.
- **Result**: TIMED OUT after 300s with no score file produced.
- **Why it timed out**: O(N * |S|) per greedy step × ~100 steps = O(10^8) operations, but the inner loop over all valid candidates (up to 10001) × computing new_diffs per candidate (O(|S|) = up to 100) × 100 steps ≈ 10^8 Python operations ≈ 100-1000s. Python is too slow for this algorithm at N=10000.
- **Conclusion**: The algorithm is correct but needs NumPy vectorization or C implementation to run in time.

## Key Findings

1. **Track B (non-Singer) is fundamentally harder**: Singer achieves 102 by exploiting perfect algebraic structure. Non-algebraic approaches like random greedy get 63-66. The gap is large.

2. **Alteration method fails**: Starting from random subsets and removing violations reaches only ~63 — below even deterministic greedy (66). The random core has no algebraic structure to preserve.

3. **Min-blocking greedy is promising in theory but too slow for Python**: It needs either C/numpy implementation or a smarter representation. The key insight — greedy that minimizes future damage — should outperform pure greedy, but we couldn't verify this.

4. **Singer is provably near-optimal**: For N=10000, Singer(101) gives 102 elements, which is near the theoretical bound (√2N ≈ 141, but perfect difference set bound ≈ √N ≈ 100-103). Getting to 109 likely requires ILP/CP-SAT.

## Unexplored Directions

- **OR-Tools CP-SAT**: ILP solver could potentially find 103+. Not tried due to time constraints.
- **Min-blocking greedy with numpy**: Same algorithm but vectorized — should run in ~1s.
- **Sidon sets from elliptic curves**: Cilleruelo (2011) construction, not attempted.
- **Large-k perturbation of Singer base**: Remove 40+ elements and rebuild with backtracking. Untested.

## Hypotheses About Dead Ends

- The probabilistic alteration method is a known technique that in practice gives at most ~0.9 × greedy performance. It's not a new basin.
- Min-blocking greedy likely gives 70-85 (better than pure greedy but well below Singer). It explores the same "non-algebraic" basin as greedy but more carefully.
