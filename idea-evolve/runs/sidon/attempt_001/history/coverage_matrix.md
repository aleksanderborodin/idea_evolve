# Coverage Matrix — Updated through Generation 7

**Scale rule: top 30 most-used ideas, sparse format (only rows with actual trials).**

## Single-Idea Coverage

| Idea | Times Central | Best Score | Avg Score | Last Tried | Status |
|------|--------------|------------|-----------|------------|--------|
| idea_008 (Singer q=101 Trunc.) | 8 | 102 | 102.0 | gen_3 | established — ceiling confirmed |
| idea_006 (Singer Difference Set) | 7 | 104 | 100.3 | gen_5 | established — q=103 mul=400 gives 104 |
| idea_002 (Local Search / LNS) | 9 | 68 | 50.6 | **gen_7** | debunked — sol02 aggressive VLNS = 65 |
| idea_011 (ET Extension + Search) | 7 | 75 | 74.9 | **gen_7** | active — **75 ceiling re-confirmed** |
| idea_004 (Modular Arithmetic) | 6 | 102 | 85.2 | gen_5 | established |
| idea_003 (Difference-Aware) | 6 | 99 | 67.5 | gen_5 | active — peripheral only |
| idea_020 (Rokicki-Dogon Rulers) | 8 | **105** | 104.6 | **gen_7** | established |
| idea_022 (Bose-Chowla AP) | 5 | **105** | 105.0 | **gen_7** | established |
| idea_023 (Multiplier Optimization) | 5 | **105** | 104.2 | gen_5 | established |
| idea_021 (Beam Search Greedy) | 7 | 70 | 67.7 | gen_5 | archived — ceiling 70 |
| idea_019 (CP-SAT ILP) | 6 | 102 | 103.2 | **gen_7** | active — 4 gens, zero improvement |
| idea_009 (Erdos-Turan) | 7 | 75 | 73.5 | gen_6 | established — ceiling 75 |
| idea_007 (Singer Perturbation q=97) | 4 | 99 | 99.0 | gen_2 | established — ceiling 99, STALE |
| idea_001 (Randomized Greedy) | 5 | 66 | 56.0 | **gen_7** | debunked — sol02 = 65 |
| idea_016 (Min-Blocking Greedy) | 3 | 69 | 45.7 | gen_4 | archived — ceiling 69 |
| idea_012 (Singer q=101 Perturbation) | 3 | 102 | 102.0 | gen_3 | debunked |
| idea_010 (SA from Algebraic Seed) | 3 | 102 | 101.0 | gen_3 | debunked |
| idea_015 (Fibonacci Ordering) | 1 | 69 | 69.0 | gen_3 | archived — ceiling confirmed |
| idea_017 (Large-k Perturbation) | 1 | 102 | 102.0 | gen_3 | debunked |
| idea_018 (SA + Violation Relaxation) | 1 | 68 | 68.0 | gen_3 | debunked |
| idea_014 (Probabilistic Alteration) | 1 | 63 | 63.0 | gen_3 | debunked |
| idea_013 (Multi-Singer Hybrid) | 1 | 0 | 0.0 | gen_4 | debunked |
| idea_005 (Backtracking + Pruning) | 1 | 66 | 66.0 | gen_6 | debunked — DFS IS greedy |
| idea_024 (VLNS) | 3 | 105 | 105.0 | **gen_7** | **established** — formulation correct, INFEASIBLE at 106 |
| idea_025 (Ruzsa-Lindström) | 2 | **75** | 74.5 | **gen_7** | **NEW GEN 7** — basin ceiling = 75, same as ET |

## Multi-Idea Combination Coverage

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|-----------------|-------------|------------|-----------|------------|
| idea_020 + idea_022 (Rokicki-Dogon + Bose-Chowla) | 5 | **105** | 105.0 | **gen_7** |
| idea_020 + idea_022 + idea_024 (Rokicki + BC + VLNS) | 2 | 105 | 105.0 | **gen_7** |
| idea_020 + idea_006 + idea_023 (Rokicki + Singer + mul opt) | 3 | **104** | 103.7 | gen_5 |
| idea_019 + idea_020 (CP-SAT k=106 + 105-mark hint) | 3 | 105 | 105.0 | gen_6 |
| idea_019 + idea_024 (CP-SAT + VLNS) | 2 | 105 | 105.0 | **gen_7** |
| idea_019 + idea_008 (CP-SAT + Singer hint) | 2 | 102 | 102.0 | gen_5 |
| idea_025 + idea_011 (Ruzsa + ET extension + VLNS) | 2 | **75** | 74.5 | **gen_7** |
| idea_011 + idea_009 (ET + Extension + LNS) | 6 | 75 | 74.8 | gen_6 |
| idea_001 + idea_002 (Random greedy + aggressive VLNS) | 1 | 65 | 65.0 | **gen_7** |
| idea_008 + idea_017 (Singer q=101 + large-k perturb) | 1 | 102 | 102.0 | gen_3 |
| idea_008 + idea_012 (Singer q=101 + small-k perturb) | 3 | 102 | 102.0 | gen_2-3 |
| idea_008 + idea_010 (Singer q=101 + SA) | 2 | 102 | 102.0 | gen_2-3 |
| idea_006 + idea_007 (Singer q=97 + perturbation) | 3 | 99 | 99.0 | gen_1 |
| idea_016 + idea_003 (Min-blocking + diff-aware) | 2 | 69 | 68.5 | gen_4 |

## Unexplored Promising Combinations

| Combination | Rationale | Priority |
|-------------|-----------|----------|
| idea_019 maximize formulation (binary x_i, max Σx_i) | Only untested CP-SAT formulation. 4h+ runtime needed. | **HIGH** |
| idea_019 anti-algebraic (force ≤52 overlap with BEST_105) | Explores non-algebraic basin. | Medium |
| Tabu search (swap-then-fill) from BEST_105 | Prevents self-healing return. Best untried heuristic per literature. | Medium |
| idea_024 VLNS from non-BEST_105 seed (e.g., Singer q=103 104-mark) | Test if self-healing is BEST_105-specific. | Medium |
