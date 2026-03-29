# Constraints

## Hard Constraints
- Each row must be a valid permutation of {0, 1, ..., n-1} (n=8)
- All pairwise Hamming distances must be ≥ d (d=5)
- No duplicate rows (each permutation appears at most once)
- All values must be integers in range [0, n-1]
- Array must be 2D with shape (K, n) where K ≥ 1

## Soft Constraints
- Use numpy, scipy, itertools, or standard library
- Fix random seeds for reproducibility
- Solutions must implement `def entrypoint() -> np.ndarray`
- Prefer constructions that run in under 30 seconds

## Environment
- Python 3.12
- NumPy available
- SciPy available
- itertools, collections, functools available
- Standard library available

## Problem Parameters
- n = 8 (permutation length)
- d = 5 (minimum Hamming distance)
- Total permutations: 8! = 40320
- Known bounds: 616 ≤ M(8,5) ≤ 926
