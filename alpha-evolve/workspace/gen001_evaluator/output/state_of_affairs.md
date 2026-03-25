---
generation: 1
best_score: 1.5168
trajectory: improving
last_updated_gen: 1
---

# State of Affairs — Generation 1

## Current Standing

Best score: **C = 1.5168** (explore_1/sol12, aggressive basin hopping with multi-scale Adam).
Baseline was 1.5185; best improvement is 0.0017. Target is C <= 1.5053, so we need another
0.0115 reduction. The known best upper bound in the literature is C <= 1.5098, meaning the
target is 0.0045 below the best published result.

30 solutions were produced across 3 solution agents (explore_1, explore_2, full_1) and 1
research agent. Of 30 solutions, 27 are valid with fitness < 2.0, and 15 beat the baseline
of 1.5185. The top 5 solutions all come from explore_1 and use multi-scale Adam optimization:

| Rank | Solution | Score | Key Ideas |
|------|----------|-------|-----------|
| 1 | explore_1/sol12 | 1.5168 | Multi-scale + aggressive basin hopping |
| 2 | explore_1/sol11 | 1.5168 | Multi-scale + basin hopping (5 rounds) |
| 3 | explore_1/sol09 | 1.5174 | Multi-scale + multi-start (5 diverse inits) |
| 4 | explore_1/sol06 | 1.5176 | Three-phase multi-scale (N=600->2000->4000) |
| 5 | explore_1/sol05 | 1.5177 | Extended multi-scale + multiple seeds |

## What Works

**Multi-scale Adam optimization** (idea_004) is the foundational technique. Every solution
scoring below 1.518 uses it. The standard pipeline: N=600 (40k steps) -> upsample -> N=2000
(50-80k steps). Adding **basin hopping** (idea_007) on top provides a further ~0.001 improvement.

**What does NOT work:**
- L-BFGS from cold start (C ~ 1.69-1.81)
- Symmetric unimodal initialization (C ~ 2.0 — proven dead end)
- TV regularization (C = 1.535)
- B-spline basis parameterization (C = 1.578)
- L1-normalized optimization (C = 1.520)

## Coverage Map

Two clusters emerged:
- **Cluster 1 (Numerical optimization pipeline)**: Well-explored. Adam + multi-scale + basin
  hopping is near its ceiling at C ~ 1.5168.
- **Cluster 2 (Function structure and initialization)**: UNEXPLORED. Research_1 identified
  that multi-bump/Sidon-set initializations could access fundamentally better basins, and
  that symmetry enforcement + bimodal init is theoretically motivated. Zero solutions test these.

## Dead Ends

- Symmetric unimodal functions (pattern_001, C = 2.0)
- L-BFGS as primary optimizer from scratch (pattern_003, C = 1.69-1.81)
- TV regularization annealing (C = 1.535)

## Open Questions

1. **Can multi-bump initializations break the 1.5168 floor?** This is the #1 question.
   Research predicts bimodal/Sidon-set inits access different basins.
2. **Does softplus reparameterization help?** Tested only with L-BFGS (confounded). Needs
   Adam test to isolate the effect.
3. **What does the current best function look like?** Is it unimodal? If so, the theory
   predicts a bimodal function could do better.
4. **Can we reach C <= 1.5098 (published bound)?** This would confirm our optimization
   matches the state of the art. Then we'd need novel math to go below.
5. **Is the optimal function multi-bump? How many bumps?** Determines initialization strategy.
