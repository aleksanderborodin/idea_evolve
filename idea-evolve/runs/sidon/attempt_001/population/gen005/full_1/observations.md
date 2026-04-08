# Observations — gen005_full_1

## Solutions

| File | Fitness | Approach |
|------|---------|----------|
| sol01.py | **102** | Singer q=101 baseline (CP-SAT found nothing better) |

## Part A: Singer+1 Structure Analysis

Ran CP-SAT on small-N cases to compare Singer vs optimal Sidon sets.

### Results

| q | N | Singer | Optimal | Overlap | Notes |
|---|---|--------|---------|---------|-------|
| 7 | 56 | 8 | **10** | 3 | k=11 proved INFEASIBLE |
| 11 | 132 | 12 | **13** | 1 | k=14 UNKNOWN at 60s |
| 17 | 306 | 18 | 18 | 18 | k=19 UNKNOWN at 120s |
| 23 | 552 | 24 | 24 | 24 | k=25 UNKNOWN at 120s |

### Key Insight

For q=7: optimal set is [0,1,6,10,23,26,34,41,53,55] — shares only **3** of 8 Singer elements.
For q=11: optimal set shares only **1** of 12 Singer elements.

The optimal sets are NOT perturbations of Singer. They are structurally unrelated. This suggests:
1. Singer hint may actively hurt CP-SAT by pointing to the wrong region.
2. True optimal for N=10000 might be above 103 (if Singer is ~8-25% suboptimal at small N).
3. The extra elements do NOT use only "free" differences — they require replacing Singer elements entirely.

## Part B: Extended CP-SAT for k=103

Three 600s phases, all UNKNOWN:

| Phase | Strategy | Hint | Workers | Time | Result |
|-------|----------|------|---------|------|--------|
| 1 | portfolio | none | 16 | 600s | UNKNOWN |
| 2 | portfolio | partial Singer (51 elems) | 16 | 600s | UNKNOWN |
| 3 | auto | full Singer (102 elems) | 16 | ~600s | UNKNOWN (terminated) |

CP-SAT presolve found 102 affine relations and 101 redundant constraints, reducing to 5253 variables. The search tree made progress (hundreds of nodes) but found no feasible k=103 set.

## Conclusions

- **Score: 102** (no improvement)
- CP-SAT cannot find k=103 in 1800s across 3 different search strategies
- Singer hint vs no-hint makes no difference to CP-SAT outcome
- Small-N analysis suggests Singer is genuinely suboptimal — the full-N optimal likely exists but requires different search methods
- Recommend: Gurobi/CPLEX trial, or reduce N to find smallest N where k=103 is feasible
