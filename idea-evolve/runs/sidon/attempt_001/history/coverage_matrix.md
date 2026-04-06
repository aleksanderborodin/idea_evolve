# Coverage Matrix — Updated through Generation 4

**Scale rule: top 30 most-used ideas, sparse format (only rows with actual trials).**

## Single-Idea Coverage

| Idea | Times Central | Best Score | Avg Score | Last Tried | Status |
|------|--------------|------------|-----------|------------|--------|
| idea_008 (Singer q=101 Trunc.) | 8 | 102 | 102.0 | gen_3 | established — ceiling confirmed |
| idea_006 (Singer Difference Set) | 5 | 102 | 99.6 | gen_4 | established — q=103 tested, no improvement |
| idea_007 (Singer Perturbation q=97) | 4 | 99 | 99.0 | gen_2 | established — ceiling 99 |
| idea_002 (Local Search / LNS) | 8 | 68 | 51.1 | gen_3 | disputed — marginal gains only |
| idea_001 (Randomized Greedy) | 3 | 66 | 54.0 | gen_3 | debunked |
| idea_009 (Erdos-Turan) | 4 | 75 | 73.5 | gen_2 | established — ceiling 75 |
| idea_011 (ET Extension + Search) | 3 | 75 | 74.7 | gen_2 | active |
| idea_004 (Modular Arithmetic) | 5 | 102 | 101.2 | gen_3 | established |
| idea_010 (SA from Algebraic Seed) | 3 | 102 | 101.0 | gen_3 | debunked |
| idea_012 (Singer q=101 Perturbation) | 3 | 102 | 102.0 | gen_3 | debunked |
| idea_003 (Difference-Aware) | 5 | 99 | 81.0 | gen_4 | active — peripheral support only |
| idea_014 (Probabilistic Alteration) | 1 | 63 | 63.0 | gen_3 | debunked |
| idea_015 (Fibonacci Ordering) | 1 | 69 | 69.0 | gen_3 | active — ceiling confirmed by pattern_011 |
| idea_016 (Min-Blocking Greedy) | 3 | 69 | 45.7 | gen_4 | active — corrected impl ceiling 69 |
| idea_017 (Large-k Perturbation) | 1 | 102 | 102.0 | gen_3 | debunked |
| idea_018 (SA + Violation Relaxation) | 1 | 68 | 68.0 | gen_3 | debunked |
| idea_013 (Multi-Singer Hybrid) | 1 | 0 | 0.0 | gen_4 | **DEBUNKED** — experimentator tested, zero gain |
| idea_019 (CP-SAT ILP) | 1 | 102 | 102.0 | gen_4 | **NEW** — UNKNOWN for k=103, not disproved |
| idea_020 (Rokicki-Dogon Rulers) | 0 | -- | -- | never | **NEW, UNTESTED** — database found but not parsed |
| idea_005 (Backtracking + Pruning) | 0 | -- | -- | never | **UNTESTED** |

## Multi-Idea Combination Coverage

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|-----------------|-------------|------------|-----------|------------|
| idea_019 + idea_008 (CP-SAT + Singer hint) | 1 | 102 | 102.0 | gen_4 |
| idea_008 + idea_017 (Singer q=101 + large-k perturb) | 1 | 102 | 102.0 | gen_3 |
| idea_008 + idea_012 (Singer q=101 + small-k perturb) | 3 | 102 | 102.0 | gen_2-3 |
| idea_008 + idea_010 (Singer q=101 + SA) | 2 | 102 | 102.0 | gen_2-3 |
| idea_006 + idea_007 (Singer q=97 + perturbation) | 3 | 99 | 99.0 | gen_1 |
| idea_006 + idea_008 (Singer q=103 + truncation) | 1 | 102 | 102.0 | gen_4 |
| idea_007 + idea_010 (q=97 perturb + SA) | 1 | 99 | 99.0 | gen_2 |
| idea_009 + idea_011 (ET + Extension) | 3 | 75 | 74.7 | gen_2 |
| idea_016 + idea_003 (Min-blocking + diff-aware) | 2 | 69 | 68.5 | gen_4 |
| idea_015 + idea_018 (Fibonacci + SA) | 1 | 68 | 68.0 | gen_3 |
| idea_015 + idea_002 (Fibonacci + LNS) | 1 | 69 | 69.0 | gen_3 |
| idea_001 + idea_002 (Random greedy + ILS) | 1 | 66 | 66.0 | gen_1 |

## Unexplored Promising Combinations

| Combination | Rationale | Priority |
|-------------|-----------|----------|
| idea_020 (Rokicki-Dogon mark lists) | Download and parse cube20.org database. Direct 104-105 score if mark lists exist. | **CRITICAL** |
| idea_019 extended run (CP-SAT 4h+) | k=103 UNKNOWN in 600s. Longer run or commercial solver needed. | **HIGH** |
| idea_019 + idea_020 (ILP + Rokicki seed) | Use Rokicki mark list as CP-SAT hint for k=105+ | **HIGH** |
| Beam search greedy (not yet an idea) | Multiple agents suggest k=20-50 beams. Could reach 75-85. | Medium |
| idea_005 (Backtracking + Pruning) | Never tested at any scale. | Low |
