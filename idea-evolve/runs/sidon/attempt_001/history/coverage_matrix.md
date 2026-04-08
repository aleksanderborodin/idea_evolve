# Coverage Matrix — Updated through Generation 6

**Scale rule: top 30 most-used ideas, sparse format (only rows with actual trials).**

## Single-Idea Coverage

| Idea | Times Central | Best Score | Avg Score | Last Tried | Status |
|------|--------------|------------|-----------|------------|--------|
| idea_008 (Singer q=101 Trunc.) | 8 | 102 | 102.0 | gen_3 | established — ceiling confirmed |
| idea_006 (Singer Difference Set) | 7 | 104 | 100.3 | gen_5 | established — q=103 mul=400 gives 104 |
| idea_002 (Local Search / LNS) | 8 | 68 | 51.1 | gen_3 | debunked |
| idea_011 (ET Extension + Search) | 6 | 75 | 74.8 | **gen_6** | active — **75 hard ceiling confirmed** |
| idea_004 (Modular Arithmetic) | 6 | 102 | 85.2 | gen_5 | established |
| idea_003 (Difference-Aware) | 6 | 99 | 67.5 | gen_5 | active — peripheral only |
| idea_020 (Rokicki-Dogon Rulers) | 7 | **105** | 104.6 | **gen_6** | established |
| idea_022 (Bose-Chowla AP) | 4 | **105** | 105.0 | **gen_6** | established |
| idea_023 (Multiplier Optimization) | 5 | **105** | 104.2 | gen_5 | established |
| idea_021 (Beam Search Greedy) | 7 | 70 | 67.7 | gen_5 | active — ceiling 70 |
| idea_019 (CP-SAT ILP) | 5 | 102 | 103.4 | **gen_6** | active — k=106 UNKNOWN 3 gens |
| idea_009 (Erdos-Turan) | 7 | 75 | 73.5 | **gen_6** | established — ceiling 75 |
| idea_007 (Singer Perturbation q=97) | 4 | 99 | 99.0 | gen_2 | established — ceiling 99 |
| idea_001 (Randomized Greedy) | 4 | 66 | 55.8 | **gen_6** | debunked |
| idea_016 (Min-Blocking Greedy) | 3 | 69 | 45.7 | gen_4 | active — ceiling 69 |
| idea_012 (Singer q=101 Perturbation) | 3 | 102 | 102.0 | gen_3 | debunked |
| idea_010 (SA from Algebraic Seed) | 3 | 102 | 101.0 | gen_3 | debunked |
| idea_015 (Fibonacci Ordering) | 1 | 69 | 69.0 | gen_3 | active — ceiling confirmed |
| idea_017 (Large-k Perturbation) | 1 | 102 | 102.0 | gen_3 | debunked |
| idea_018 (SA + Violation Relaxation) | 1 | 68 | 68.0 | gen_3 | debunked |
| idea_014 (Probabilistic Alteration) | 1 | 63 | 63.0 | gen_3 | debunked |
| idea_013 (Multi-Singer Hybrid) | 1 | 0 | 0.0 | gen_4 | debunked |
| idea_005 (Backtracking + Pruning) | 1 | 66 | 66.0 | **gen_6** | **DEBUNKED** — DFS IS greedy |
| idea_024 (VLNS) | 1 | 105 | 105.0 | **gen_6** | **NEW** — formulation bug, needs fix |
| idea_025 (Ruzsa-Lindström) | 0 | -- | -- | never | **NEW, UNTESTED** |

## Multi-Idea Combination Coverage

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|-----------------|-------------|------------|-----------|------------|
| idea_020 + idea_022 (Rokicki-Dogon + Bose-Chowla) | 4 | **105** | 105.0 | gen_6 |
| idea_020 + idea_006 + idea_023 (Rokicki + Singer + mul opt) | 3 | **104** | 103.7 | gen_5 |
| idea_019 + idea_020 (CP-SAT k=106 + 105-mark hint) | 3 | 105 | 105.0 | **gen_6** |
| idea_019 + idea_008 (CP-SAT + Singer hint) | 2 | 102 | 102.0 | gen_5 |
| idea_024 + idea_020 (VLNS + fixed 105-mark subset) | 1 | 105 | 105.0 | **gen_6** |
| idea_011 + idea_009 (ET + Extension + LNS) | 6 | 75 | 74.8 | **gen_6** |
| idea_008 + idea_017 (Singer q=101 + large-k perturb) | 1 | 102 | 102.0 | gen_3 |
| idea_008 + idea_012 (Singer q=101 + small-k perturb) | 3 | 102 | 102.0 | gen_2-3 |
| idea_008 + idea_010 (Singer q=101 + SA) | 2 | 102 | 102.0 | gen_2-3 |
| idea_006 + idea_007 (Singer q=97 + perturbation) | 3 | 99 | 99.0 | gen_1 |
| idea_016 + idea_003 (Min-blocking + diff-aware) | 2 | 69 | 68.5 | gen_4 |

## Unexplored Promising Combinations

| Combination | Rationale | Priority |
|-------------|-----------|----------|
| idea_024 (VLNS, fixed formulation) + idea_020 | Fix domain bug, retry with 50+ patterns. Cheap per trial. | **CRITICAL** |
| idea_019 maximize formulation + idea_020 | Maximize k instead of decision for fixed k=106. More solver-friendly. | **HIGH** |
| idea_025 + idea_010 (Ruzsa-Lindström + SA) | Different algebraic seed may reach different local optima | Medium |
| idea_019 overnight (4h+) + idea_020 | Longer solver time may find k=106 | Medium |
| Alternative solvers (Gurobi, SCIP) + idea_019 formulation | Different solver technology | Medium |
