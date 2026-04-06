# Initial Ideas for Sidon Sets

## idea_001: Randomized Greedy with Restarts
The basic greedy algorithm always adds the smallest valid element, giving 66.
Try random orderings of candidates: shuffle the range [0, 10000] and greedily
add elements that don't violate the Sidon property. Run many restarts and keep
the best. Different random orderings explore different parts of the search space.

## idea_002: Local Search (Swap Neighborhood)
Start from a greedy Sidon set. Define neighborhood: remove one element, try
adding a different one. Accept if the set grows or stays same size with more
room for future additions. Iterate until no improvement. Can be combined with
simulated annealing to escape local optima.

## idea_003: Difference-Aware Construction
Instead of checking violations after the fact, maintain the set of used differences
explicitly. When choosing the next element to add, pick one that uses "rare"
differences (large gaps in the difference spectrum). This leaves more room for
future elements.

## idea_004: Modular Arithmetic Structure
Elements chosen with modular structure (e.g., quadratic residues, powers modulo
a prime) tend to have good difference properties. Explore sets of the form
{f(k) mod N : k in range} for various functions f. The structure provides a
scaffold that can then be improved by local search.

## idea_005: Backtracking with Pruning
Use depth-first search with aggressive pruning: at each step, count how many
candidates remain that could be added without violation. If the count drops
below (target - current_size), backtrack. This prunes hopeless branches early.
