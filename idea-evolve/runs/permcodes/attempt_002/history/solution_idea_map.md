# Solution-Idea Map

## Generation 1

### Solution: gen001_explore_1_sol01 (score: 616, valid)
- Central: idea_001 (AGL(1,8) orbit clique search)
- Peripheral: idea_002 (degree-ordered greedy vertex selection)
- Novel elements: Exhaustive search over all 720 starting vertices to confirm 11-orbit optimum

### Solution: gen001_explore_1_sol02 (score: 616, valid)
- Central: idea_001 (AGL(1,8) orbit clique search)
- Peripheral: idea_003 (individual permutation extension attempt)
- Novel elements: Attempted to extend orbit clique with non-orbit permutations; found 0 compatible

### Solution: gen001_explore_1_sol03 (score: 616, valid)
- Central: idea_001 (AGL(1,8) orbit clique search)
- Peripheral: idea_004 (randomized perturbation / random restart)
- Novel elements: Randomized perturbation from known 11-orbit clique; 500 iterations found no improvement

### Solution: gen001_explore_1_sol04 (score: 262, valid)
- Central: idea_005 (direct greedy on full 40320-permutation space)
- Peripheral: none
- Novel elements: None — pure baseline greedy; used random ordering with 50 restarts

### Solution: gen001_explore_2_sol01 (score: 290, valid)
- Central: idea_006 (Iterated Large Neighborhood Search / ILNS)
- Peripheral: idea_007 (1-opt intensification), idea_008 (bucket-based compatibility pruning)
- Novel elements: First ILNS attempt; 8 restarts × 300 iterations, destroy 20-40%

### Solution: gen001_explore_2_sol02 (score: 284, valid)
- Central: idea_006 (ILNS)
- Peripheral: idea_009 (tabu-style diversification), idea_008 (bucket-based compatibility)
- Novel elements: More aggressive ILNS — 20 restarts × 600 iterations, destroy 30-50%

### Solution: gen001_explore_2_sol03 (score: 0, INVALID — bug: dtype error in make_code_compatible)
- Central: idea_010 (Genetic Algorithm with crossover)
- Peripheral: idea_008 (bucket-based compatibility)
- Novel elements: GA crossover operator — failed due to np.array([]) dtype=float64 default
- Bug: This solution is INVALID and should not inform future decisions

### Solution: gen001_explore_2_sol04 (score: 0, INVALID — timeout bug)
- Central: idea_006 (ILNS)
- Novel elements: Simplified ILNS with fixed greedy bug — returned all 40320 permutations (timeout)
- Bug: greedy_with_order had logic error; solution is INVALID

### Solution: gen001_explore_2_sol05 (score: 293, valid)
- Central: idea_006 (ILNS)
- Peripheral: idea_008 (bucket-based compatibility)
- Novel elements: Fixed greedy + destroy/repair; best ILNS result (15 restarts × 400 iterations)

### Solution: gen001_full_1_sol01 (score: 616, valid)
- Central: idea_001 (AGL(1,8) orbit clique search)
- Peripheral: none
- Novel elements: Direct call to agl18_max_clique_code() helper

### Solution: gen001_full_1_sol02 (score: 616, valid)
- Central: idea_001 (AGL(1,8) orbit clique search)
- Peripheral: idea_003 (individual permutation extension)
- Novel elements: Tried to find compatible permutations outside orbit clique; found 0 extensions

### Solution: gen001_full_1_sol03 (score: 616, valid)
- Central: idea_001 (AGL(1,8) orbit clique search)
- Peripheral: idea_011 (multi-seed clique search with 500 starting orderings)
- Novel elements: Confirmed 11-orbit clique is unique optimum across 500 different orderings

---

## Novel Elements Not Yet Captured as Ideas

- **AGL orbit clique maximality**: The 616-code (11 orbits) appears to be exactly maximal — no individual permutation outside the 11 orbits is compatible with all 616 codewords. This is a strong empirical finding that should inform the search strategy.
- **ILNS caps at ~290-293**: Stochastic search without algebraic structure cannot approach 616. The bucket structure (70 bucket IDs) is necessary but not sufficient.
- **GA crossover ineffective**: Combining two partial codes via union+prune loses too many codewords due to incompatibility. Crossover operator needs redesign.
