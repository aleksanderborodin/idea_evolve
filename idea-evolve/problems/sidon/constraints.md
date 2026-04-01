# Constraints

1. `entrypoint()` must return a list of integers
2. All elements must be in range [0, 10000]
3. All elements must be distinct
4. The Sidon property: all pairwise sums a+b (a <= b, a,b in S) must be distinct
5. Equivalently: all positive differences b-a (a < b, a,b in S) must be distinct
6. Solution must complete within 30 seconds
7. No external network access or file I/O beyond the solution file itself
