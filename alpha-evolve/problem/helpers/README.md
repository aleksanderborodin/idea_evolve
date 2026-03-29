# Problem Helpers

All reusable helpers live here. Import them in solution files as:

    from helpers.<module> import <function>

## Available Helpers

### core.py — Permutation code utilities
- `hamming_distance(p, q)` → int: Hamming distance between two permutations
- `min_distance(perms)` → int: Minimum pairwise distance in a code
- `check_code(perms, d)` → (bool, int): Validate code and return size
- `pairwise_distances(perms)` → np.ndarray: Full distance matrix (K×K)
- `compatible_permutations(perms, d, n=8)` → np.ndarray: All perms of {0,...,n-1}
  compatible with existing code (WARNING: enumerates all n! permutations, slow for n>8)
