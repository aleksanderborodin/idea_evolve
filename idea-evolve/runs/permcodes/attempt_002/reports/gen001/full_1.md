# Debrief — full_1, Generation 1

## What Did You Try?

1. **AGL(1,8) baseline (sol01.py)**: Called `agl18_max_clique_code()` directly.
   - Result: 616 codewords, fitness = 616, is_valid = 1.
   - This matches the known lower bound from Smith & Montemanni (2012).

2. **Extension attempt beyond 616 (sol02.py)**: Used bucket-based fast compatibility check
   to find permutations outside the 616-code that are compatible with all 616 codewords.
   - Result: 0 extension candidates found. The 616-code is orbit-maximal.
   - Fitness = 616 (no improvement).

3. **Multi-seed clique search (sol03.py)**: Ran max-clique search with 500 different random
   starting orderings to try to find a larger orbit clique.
   - Result: Always found exactly 11 orbits (616). The max clique is 11 orbits.
   - Fitness = 616.

## What Information Did You Lack?

- No knowledge of whether PGL(2,7), PSL(2,7), or other groups have been tried on this problem.
- No information about whether extending the AGL code with non-orbit permutations was attempted in prior work.
- No cluster summaries or idea files existed yet to learn from other agents.

## Was the State of Affairs Accurate?

- This was gen 0, so State of Affairs correctly noted "nothing explored yet."
- N/A for this generation.

## What Would You Do Differently?

- Immediately try PGL(2,7) construction if AGL(1,8) maxes out at 616.
- Try the `compat.compatible_mask()` approach on a larger search (not just greedy extension).
- Investigate whether there are asymmetric orbits or non-orbit permutations that could extend the code.
- Try simulated annealing on the full 40320-permutation space rather than just the orbit graph.

## Specific Experiments to Run

1. **PGL(2,7) construction**: Build PGL(2,7) permutations and search for maximum clique in
   combined PGL+AGL orbit graph.
2. **Full space SA**: Run simulated annealing on the full permutation space to escape the
   local maxima at 616.
3. **Different orbit partition**: Try PGL(2,7) orbits (different size than AGL's 56-element
   orbits) and build compatibility graph across different group structures.
4. **Backtracking max-clique**: Implement Bron–Kerbosch or branch-and-bound max-clique on
   the orbit graph instead of greedy to verify 11 is truly maximum.

## What Surprised You?

- The 616-code appears to be exactly maximal within the AGL orbit structure — no seed found
  a larger clique despite 500 attempts.
- The greedy max-clique algorithm is heavily dependent on starting vertex order; many seeds
  produce the same 11-orbit result.

## Helper Tools Feedback

- `agl18_max_clique_code()`: Worked correctly, returns 616.
- `fast_compatible_mask()`: Fast and correct (0.2s for full 40320-element mask).
- `build_all_perms()`: Correct but slow (enumerates all 40320 permutations).
- No bugs found. Helpers are accurate and well-documented.

## Time Budget

- Had sufficient time for 3 solution attempts.
- If more time: implement Bron–Kerbosch max-clique on orbit graph to verify optimality,
  and try PGL(2,7) construction.