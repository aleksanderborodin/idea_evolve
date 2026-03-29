# Permutation Codes — Maximize Code Size M(n,d)

## Challenge
Combinatorial optimization in coding theory. Construct the largest possible set of
permutations of {0, 1, ..., n-1} such that every pair of permutations has Hamming
distance at least d.

**Current target: M(8, 5)** — maximize the number of permutations of {0,...,7} with
pairwise Hamming distance ≥ 5.

**Known bounds:** 616 ≤ M(8,5) ≤ 926 (Smith & Montemanni, 2012).
Any code with more than 616 permutations is a new result.

## Objective
Return a 2D NumPy array of permutations such that:
1. **(Valid permutations)** Each row is a permutation of {0, 1, ..., n-1}
2. **(Minimum distance)** Every pair of rows has Hamming distance ≥ d
3. **(Maximality)** The number of rows (code size) is maximized

## Parameters
- **n = 8** — permutation length (permutations of {0, 1, ..., 7})
- **d = 5** — minimum Hamming distance between any two codewords

## Output Format
Implement `def entrypoint():` that returns a 2D NumPy array:
- Shape: (K, 8) where K is the number of codewords (permutations)
- Each row is a permutation of {0, 1, 2, 3, 4, 5, 6, 7}
- dtype: int (values 0-7)
- Return type: np.ndarray with shape (K, n)

## Scoring
- **Fitness (primary):** Code size K — the number of valid codewords. **HIGHER IS BETTER.**
- **Valid:** 1 if all permutations are valid and all pairwise distances ≥ d, 0 otherwise.
- **Goal:** fitness > 616 (beat the known lower bound)
- **Ultimate bound:** fitness ≤ 926 (theoretical upper bound)

## Hamming Distance
The Hamming distance between two permutations π and σ of {0,...,n-1} is:
  hd(π, σ) = |{i : π(i) ≠ σ(i)}|
i.e., the number of positions where the two permutations differ.

Equivalently, if they agree on exactly k positions, hd = n - k.
For d=5 and n=8: any two codewords may agree on at most 3 positions.

## Known Construction Methods
- **Automorphism groups:** Use algebraic groups (AGL, PGL, PSL, Mathieu, etc.) and
  clique search on orbit graphs. Smith & Montemanni (2012) achieved M(8,5) ≥ 616
  using AGL(1,8) with 11 orbits.
- **Clique search:** Build graph G(n,d) where vertices are permutations and edges
  connect pairs with distance ≥ d. Maximum clique = largest code.
- **Greedy extension:** Start with a valid code and greedily add permutations that
  maintain the distance property.
- **Group-theoretic:** Cosets of sharply transitive groups, mutually orthogonal latin
  squares, projective planes.
- **Iterative clique building:** Start from a partial code, remove random subset,
  find compatible permutations via clique search on the residual graph, iterate.
- **Hybrid:** Combine algebraic constructions with local search optimization.

## Failure Modes to Avoid
- Duplicate permutations in the code (inflate count without adding codewords)
- Rows that are not valid permutations (missing or repeated elements)
- Pairs with Hamming distance < d (constraint violation)
- Brute force enumeration of all 8! = 40320 permutations (too slow for clique search)
- Greedy-only approaches typically plateau well below algebraic constructions

## Helper Functions
- `helpers/core.py` provides `hamming_distance(p, q)` and `check_code(perms, d)`
  - `hamming_distance(p, q)` → int: Hamming distance between two permutations
  - `check_code(perms, d)` → (bool, int): Check if code is valid and return size
  - `pairwise_distances(perms)` → np.ndarray: Matrix of all pairwise distances
  - `min_distance(perms)` → int: Minimum pairwise distance in the code
- See `helpers/README.md` for all available helpers

## Problem Complexity
The maximum clique problem on G(n,d) is NP-hard. For n=8, d=5, the graph G(8,5) has
40320 vertices (all permutations of 8 elements). Finding the maximum clique is
computationally intensive but feasible with good heuristics and algebraic structure
exploitation. The best known codes use automorphism groups to reduce the search space
from 40320 vertices to tens or hundreds of group orbits.

## Key References
- Smith & Montemanni (2012): "A new table of permutation codes" — best known bounds
  for M(n,d) with 6 ≤ n ≤ 18. Available at papers/pdf/001_Smith_Montemanni_permutation_codes_2012.pdf
- Chu, Colbourn, Dukes (2004): "Constructions for permutation codes in powerline
  communications" — algebraic methods
- Frankl & Deza (1977): "On maximal numbers of permutations with given maximal or
  minimal distance" — theoretical bounds

## Initial Programs
- `problem/initial_programs/optimize.py`: Greedy baseline construction
