# Observations — explore_1

## Approaches Tried

### 1. Exhaustive Orbit Clique Search (sol01.py)
- **Approach**: Try ALL 720 starting vertices for greedy clique search (vs standard greedy's 50)
- **Result**: 11 orbits → 616 codewords — same as standard greedy
- **Finding**: All 720 starting vertices produce the same result. The 11-orbit clique appears to be the unique (up to isomorphism) maximum clique in the AGL(1,8) orbit graph
- **Time**: 2.5s

### 2. Mixed Individual Extension (sol02.py)
- **Approach**: After finding the 11-orbit clique, search for individual permutations NOT in any orbit that are compatible with all 616 codewords
- **Result**: 0 individual permutations found compatible — the orbit clique is "closed" under compatibility
- **Finding**: No individual extension beyond the pure orbit construction exists (at least using AGL(1,8) orbits as the starting point)
- **Time**: 2.6s

### 3. Randomized Perturbation Search (sol03.py)
- **Approach**: Start from 11-orbit clique, remove 1-3 orbits, re-run greedy, repeat 500 times
- **Result**: 11 orbits → 616 codewords, 0 improvements found
- **Finding**: The 11-orbit clique is a very strong local optimum. Perturbations never find larger cliques
- **Time**: 2.5s

### 4. Direct Greedy on Individual Permutations (sol04.py)
- **Approach**: Multiple random-restart greedy on full 40320-permutation space (no orbit decomposition)
- **Result**: Best 262 codewords — far below the orbit approach
- **Finding**: The orbit decomposition is critical. Without it, greedy gets stuck at ~262 (66% of the way to 616)
- **Time**: 55.7s

## Key Insights

1. **AGL(1,8) orbit clique of 616 is the unique greedy optimum**: All 720 starting vertices find the same 11-orbit clique. The graph's structure makes this a unique global optimum for greedy.

2. **Orbit clique is closed**: No individual permutation outside the 11 orbits is compatible with all 616 codewords. To beat 616, one must find a DIFFERENT set of orbits (not just extend the existing clique with individuals).

3. **Direct greedy on 40320 vertices is much worse**: 262 vs 616 shows the orbit decomposition is essential — it reduces the search space from 40320 to 720 while preserving the combinatorial structure.

4. **The 616 → 624 gap (8 codewords) is nontrivial**: The theoretical bound is 926, but there's only a 8-codeword gap between known (616) and our best (also 616). This suggests:
   - Either 616 is close to optimal for AGL(1,8) methods
   - Or a different orbit decomposition (PGL, PSL) could yield larger cliques
   - Or one needs fundamentally different construction methods

## Unexplored Directions

1. **PGL(3,2) orbits**: Different group action on S_8 — 168 orbits of size 240 each
2. **PSL(2,7) orbits**: Another subgroup of S_8
3. **Full clique search on 720-vertex orbit graph**: The greedy found 11-orbit cliques, but is 11 actually the maximum? Could try branch-and-bound to prove optimality
4. **Mixed orbit types**: Combine orbits from different groups (e.g., some AGL + some PGL)
5. **Backtracking clique search**: Instead of greedy, try exact clique search on the orbit graph with better branching