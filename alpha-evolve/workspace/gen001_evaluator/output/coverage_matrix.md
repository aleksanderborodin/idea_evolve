# Coverage Matrix — Generation 1

## Idea Combination Coverage (sparse format, top ideas)

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|---|---|---|---|---|
| idea_001 (Adam) alone | 2 | 1.5257 | 1.5276 | gen_1 |
| idea_001 + idea_004 (multi-scale) | 2 | 1.5177 | 1.5178 | gen_1 |
| idea_001 + idea_004 + idea_007 (basin hopping) | 2 | 1.5168 | 1.5168 | gen_1 |
| idea_001 + idea_004 + idea_012 (multi-start) | 3 | 1.5174 | 1.5176 | gen_1 |
| idea_001 + idea_004 + idea_008 (L-BFGS hybrid) | 1 | 1.5178 | 1.5178 | gen_1 |
| idea_001 + idea_008 (Adam->L-BFGS) | 5 | 1.5178 | 1.5184 | gen_1 |
| idea_001 + idea_002 (higher N, no multi-scale) | 4 | 1.5179 | 1.5193 | gen_1 |
| idea_001 + idea_012 (multi-start, no multi-scale) | 2 | 1.5182 | 1.5183 | gen_1 |
| idea_001 + idea_009 (symmetry enforcement) | 3 | 2.0000 | 2.0000 | gen_1 |
| idea_001 + idea_010 (softplus) + L-BFGS | 2 | 1.6904 | 1.7508 | gen_1 |
| idea_001 + idea_005 (regularization) | 2 | 1.5203 | 1.5279 | gen_1 |
| idea_001 + idea_003 (B-spline basis) | 1 | 1.5785 | 1.5785 | gen_1 |

## Unexplored High-Priority Combinations

| Combination | Rationale |
|---|---|
| idea_004 + idea_007 + idea_011 (multi-scale + basin hopping + Sidon init) | Best pipeline + best untested init |
| idea_009 + idea_011 (symmetry + multi-bump) | Theory-motivated, avoids pattern_001 dead end |
| idea_004 + idea_010 (multi-scale + softplus) | Test reparameterization with proven pipeline |
| idea_004 + idea_007 + idea_012 (multi-scale + basin hopping + multi-start) | Combine best global search strategies |
| idea_008 + idea_007 (L-BFGS refinement + basin hopping) | Faster per-round refinement in hopping |

## Notes
- idea_011 (Sidon/multi-bump init) has ZERO coverage — highest priority gap
- idea_009 (symmetry) tested only with unimodal init (dead end); needs multi-bump combo
- idea_010 (softplus) tested only with L-BFGS (confounded); needs Adam test
