---
generation: 4
best_score: 102
trajectory: plateaued
last_updated_gen: 4
---

# State of Affairs — Generation 4

## Current Standing

Best score: **102** (Singer q=101 truncation, gen 2). Unchanged for 3 generations.
4 generations completed. ~40 solutions evaluated. Trajectory: **plateaued**.
Theoretical upper bound: **~109** (Carter, Hunter, O'Bryant). Gap: 7 elements.
Singer constructions are exhausted — no prime gives >102 for N=10000.

## What Works

- **Singer q=101 truncation** (idea_008, established, confidence 0.95): Deterministic
  102 elements. Optimal cyclic shift d=2337. This is the Singer ceiling for N=10000.
- **Singer difference sets** (idea_006, established, confidence 0.95): Foundation for all
  competitive solutions. q=101 optimal; q=103 tested gen 4, keeps only 102 in range.
- **Modular arithmetic structure** (idea_004, established, confidence 0.9): General
  algebraic principle underlying Singer and ET constructions.
- **ET(71) + local search** (idea_011, active, confidence 0.6): Best non-Singer result
  at 75 elements. Robust local optimum confirmed by 25 restarts.
- **Pattern: All greedy variants ceiling at 66-69** (pattern_011, confidence 0.85):
  Ascending, Fibonacci, min-blocking, spread-first — all converge. Structural limit.
- **Pattern: Singer perturbation provably futile** (pattern_009, confidence 0.9):
  Minimum 43 blockers (corrected from 45). No k-value perturbation can exceed 102.

## Current Frontier

The pipeline has exhausted Singer-based and greedy approaches. Two paths to 103+:

1. **CP-SAT / ILP** (idea_019, active): First working formulation. k integer variables
   + AllDifferent on differences. Proved Singer suboptimal for small N (q=7: 8->10,
   q=11: 12->13). k=103 at N=10000: **UNKNOWN** after 600s — not disproved. Needs
   longer runs (4h+) or commercial solvers (Gurobi/CPLEX).
2. **Rokicki-Dogon database** (idea_020, active): Published near-optimal Golomb rulers
   may contain 104-105 mark sets for span<=10000. Database found but zip not downloaded.
   **UNVERIFIED** — highest-priority action is to download and parse the actual mark lists.

## Coverage Map

**Well-explored (stable ceilings):**
- Singer q=101 truncation: 8 trials, ceiling 102
- Singer q=97 perturbation: 4 trials, ceiling 99
- ET(71) + local search: 3 trials, ceiling 75
- Non-algebraic greedy (all variants): 15+ trials, ceiling 69
- SA from any seed type: 4+ trials, zero improvement
- Singer perturbation all k: 4000+ trials, zero improvement
- Multi-Singer hybrid: 1 trial, zero gain (debunked)

**Untested or under-explored:**
- Rokicki-Dogon mark lists (idea_020): 0 trials — download needed
- CP-SAT extended run (4h+): 0 trials at scale
- Backtracking with pruning (idea_005): 0 trials
- Beam search greedy: 0 trials (suggested by agents, no formal idea)

## Dead Ends

- **Randomized greedy** (idea_001): 58-63, below deterministic baseline. Debunked.
- **SA from any seed** (idea_010): Zero improvement from Singer or non-algebraic seeds. Debunked.
- **Singer q=101 perturbation** (idea_012, idea_017): 43-blocker minimum. Debunked.
- **Multi-Singer hybrid** (idea_013): Zero compatible elements at base>=70. Debunked gen 4.
- **Probabilistic alteration** (idea_014): 63, below baseline. Debunked.
- **SA with violation relaxation** (idea_018): Fails for all seeds. Debunked.
- **Cluster 003 (Hybrid approaches)**: All ideas debunked or proven futile. Exhausted.

## Open Questions

1. **What is the published best Sidon set for N=10000?** Four generations of research
   agents failed to retrieve F(10000). The gap between 102 and 109 could be anywhere.
   This is the single most important unknown — it determines whether we are near or far
   from state of the art.
2. **Does the Rokicki-Dogon database actually contain 104-105 mark sets for span<=10000?**
   research_1 gen 4 found database entries but never downloaded the zip file. The claim
   is unverified. If wrong, idea_020 collapses.
3. **Is k=103 feasible at N=10000?** CP-SAT returned UNKNOWN (not INFEASIBLE). A longer
   run or better solver could resolve this. ILP proved Singer suboptimal for small N,
   giving genuine hope.
4. **DANGER: Stale fact files in facts/ directory.** fact_002 says upper bound is "~100-102"
   (WRONG: it's ~109). fact_004 says validator extracts subsets (WRONG: sentinel scoring).
   Corrected versions exist in ideas/active/ but the stale copies persist after 3
   generations of deletion recommendations. Agents must ignore facts/ originals.
5. **Do "Singer+1" solutions at small N share generalizable structure?** ILP found larger-
   than-Singer sets for N=56 and N=132. If the algebraic structure generalizes, it could
   guide construction at N=10000.
