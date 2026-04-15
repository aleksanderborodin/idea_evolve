# Debrief Report — explore_1, Generation 1

## 1. What did you try?

| Solution | Approach | Result |
|----------|----------|--------|
| sol01.py | Exhaustive orbit clique search (all 720 starting vertices) | 616 (11 orbits) |
| sol02.py | Mixed individual permutation extension beyond orbit clique | 616 (0 individuals added) |
| sol03.py | Randomized perturbation search (500 iterations) | 616 (no improvements) |
| sol04.py | Direct greedy on 40320 individual permutations | 262 |

## 2. What information did you lack?

The key missing information was whether the 11-orbit clique is the **unique maximum** in the AGL(1,8) orbit graph — or whether different orbit cliques exist with different orbit composition that could be extended with individual permutations. I also didn't know whether 616 is close to the maximum possible for AGL(1,8)-based constructions or far from it.

## 3. What given facts might be wrong or outdated?

The brief mentioned the target is 624, but the theoretical upper bound is 926. The gap of 316 suggests significant room for improvement through different construction methods. The 616 result (11 orbits × 56) matches Smith & Montemanni's known lower bound.

## 4. Was the State of Affairs accurate?

N/A — this was a cold-start generation. The State of Affairs correctly noted nothing had been explored yet.

## 5. What would you do differently with more or different context?

1. **Try different group decompositions**: PGL(3,2) has 168 orbits of size 240 each — fundamentally different structure than AGL(1,8)'s 720 orbits of size 56
2. **Branch-and-bound exact clique search**: Instead of greedy, try to prove whether 11 is the maximum clique size
3. **Look at the Smith & Montemanni paper** for construction details I might be missing
4. **Investigate why 616 appears to be a unique optimum**: The consistency of the greedy result across all 720 starting vertices is suspicious

## 6. Specific experiments to run

1. **PGL(3,2) orbit clique construction**: Partition S_8 using PGL(3,2) action, build compatibility graph, find max clique
2. **Exact clique search on 720-vertex graph**: Use branch-and-bound with degeneracy ordering to prove optimality of 11-orbit clique
3. **Mixed group orbits**: Combine AGL(1,8) and PGL(3,2) orbits in same graph
4. **Simulated annealing on orbit selection**: Instead of greedy, try probabilistic search on orbit subsets

## 7. What surprised you?

1. **All 720 starting vertices produce the same 11-orbit clique** — the orbit graph has an extremely regular structure where greedy is trapped in the same optimum regardless of starting point
2. **No individual extensions exist** — the orbit clique of 616 is "closed" under compatibility; not a single permutation outside the 11 orbits is compatible with all 616 codewords
3. **Direct greedy on 40320 vertices only gets to 262** — this is only 66% of 616, showing the orbit decomposition captures essential combinatorial structure

## 8. Helper tools feedback

The helpers were all correct and well-documented:
- `agl18.py`: Built-in orbits and compat graph work correctly. The `agl18_orbits()` + `agl18_compat_graph()` pipeline is clean.
- `compat.py`: `fast_compatible_mask()` with bucket IDs is a clever optimization. However, `compatible_mask()` has a bug — the docstring example shows `mask.sum() = 39549` but the function is actually called `compatible_mask` (not `compatible_with_code` as in the docstring example).

I did NOT use the `compatible_mask` function from compat.py due to the confusing naming. I used the exported function correctly.

## 9. Time budget

I had enough time to run all planned experiments. The exhaustive 720-vertex search only took 2.5s, so time was not a bottleneck.

If I had more time, I would have tried:
- A **branch-and-bound exact clique search** to prove optimality
- The **PGL(3,2) decomposition** as a fundamentally different group action
- **Genetic algorithm** approach with crossover between orbit cliques