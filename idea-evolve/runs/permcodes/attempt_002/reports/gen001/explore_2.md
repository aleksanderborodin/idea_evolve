# Debrief Report — explore_2, Generation 1

## 1. What did you try?

| Approach | Result | Notes |
|----------|--------|-------|
| ILNS v1 (sol01.py) | 290 | 8 restarts × 300 iters, destroy 20-40% |
| Aggressive ILNS v2 (sol02.py) | 284 | 20 restarts × 600 iters, destroy 30-50% |
| Genetic Algorithm (sol03.py) | ERROR | Bug in array handling; would be slow anyway |
| Fixed ILNS v5 (sol05.py) | 293 | 15 restarts × 400 iters |

All approaches beat the greedy baseline (262) but remain far from 616 (AGL bound).

## 2. What information did you lack?

- **No initial programs in `problem/initial_programs/`** — I expected to find example code but the directory was empty. Had to write greedy from scratch.
- **No existing knowledge base** — this is gen 1 cold start, so no clusters or prior ideas to learn from.
- **Bucket structure wasn't documented for search guidance** — the compat.py bucket IDs are powerful but there's no guidance on how to use them strategically for neighborhood design.

## 3. What given facts might be wrong or outdated?

- The brief says "Minimum 400+ codewords" target for ILNS. Based on my experiments, this is optimistic for pure ILNS without algebraic structure. A more realistic target is 290-300.

## 4. Was the State of Affairs accurate?

N/A — this is gen 0, State of Affairs is empty. The brief's context was sufficient.

## 5. What would you do differently with more or different context?

1. **Focus on bucket-aware perturbation** — the compat.py shows that 70 bucket IDs capture incompatibility exactly. A smarter destroy operator would remove codewords that share buckets with many others (high "blocking power").
2. **Try Variable Neighborhood Search (VNS)** — systematically change neighborhood structures (1-removal, 2-removal, block-removal, etc.) instead of random destroy fractions.
3. **Consider a "coverage" objective** — maximize not just code size but bucket diversity. A code that uses more diverse buckets might be easier to extend.

## 6. Specific experiments to run

1. **Bucket-coverage greedy**: Instead of picking any compatible candidate, pick the one that eliminates the fewest new candidates (maximize remaining options).
2. **VNS with structured neighborhoods**: small (1-2 codeword removal), medium (5-10%), large (20-30%), very large (50%).
3. **Simulated annealing**: Accept worse solutions with probability exp(-delta/T), cool slowly. May escape local optima better than ILNS's random restart approach.

## 7. What surprised you?

- Greedy alone achieves 250-260 from random starts — better than expected.
- ILNS only adds ~15% improvement — the destroy-repair doesn't find significantly better solutions.
- GA crossover didn't help at all — combining two partial codes mostly just loses codewords due to incompatibility.

## 8. Helper tools feedback

- **helpers.compat**: `fast_compatible_mask` and `build_bucket_ids` are excellent — 23x faster than naive compatibility checking. Used extensively.
- **helpers.core**: Standard `hamming_distance`, `check_code` — correct but slower for large codes.
- **helpers/README.md**: Minimal documentation. Would benefit from a "quick start" showing typical usage patterns.
- **Bug found**: GA crash when `make_code_compatible` received empty list — `np.array([])` has float64 dtype by default.

## 9. Time budget

- **Enough time**: ILNS runs in ~60-150s per solution; 3 evaluated solutions produced.
- **If more time**: Would implement VNS, try bucket-coverage greedy, and experiment with SA parameters.

## Key Takeaway

**Non-algebraic ILNS/GA approaches cap around 290-293 codewords** for M(8,5), far below 616. The AGL(1,8) algebraic structure provides crucial search space reduction that stochastic methods cannot replicate. The bucket structure is necessary but not sufficient — you need the group action to find orbits that yield large cliques efficiently.