---
generation: 7
best_score: 105
trajectory: plateaued
last_updated_gen: 7
---

# State of Affairs — Generation 7

## Current Standing

Best score: **105** (Bose-Chowla affine plane q=107, multiplier=433, span=9884). Achieved gen 5, held for 3 generations. 7 generations completed, ~75 solutions evaluated. Trajectory: **plateaued**.

Theoretical upper bound: **~109** (sqrt(N) + O(N^{1/4}), O'Bryant 2022). Gap: 4 elements.

**Key gen 7 result:** VLNS infeasibility at 106 is **genuine**, not a formulation bug as gen 6 believed. Three independent agents confirmed this. 85+ VLNS trials with corrected formulation, all INFEASIBLE for target 106, all OPTIMAL for target 105. The 105-mark set is algebraically rigid — for k≤44 removed elements, exactly k valid candidates exist (mathematical impossibility to improve). Pattern_016 assigns **0.90 confidence** to F₂(10000) = 105. CP-SAT returned UNKNOWN (solver limitation), not INFEASIBLE (proof), so 0.10 uncertainty remains.

## What Works

- **Bose-Chowla ap q=107, mul=433** (idea_022, established, 0.95): 105 elements, pipeline best. Self-healing: removing any k elements always recovers to 105 (27K+ trials, pattern_014).
- **VLNS confirms rigidity** (idea_024, established, 0.85): 85+ trials prove 106 INFEASIBLE from any 105-mark subset. cpsat.py helper now available.
- **Singer pp q=103, mul=400** (idea_006+idea_023, established): 104 elements. Second-best algebraic.
- **Singer pp q=101** (idea_008, established, 0.95): 102 elements. Third-best.
- **105 is algebraic ceiling** (pattern_012, confirmed, 0.95): Exhaustive search over all primes q≤109, both construction types, all multipliers.
- **All greedy/search methods ceiling 66-75** (cluster_002, exhausted): Beam search 70, ET(71)+search 75.

## Current Frontier

All algebraic constructions and perturbation methods exhausted. Remaining avenues:

1. **Binary maximize-k CP-SAT** (idea_019, active): Only untested CP-SAT formulation. Binary variables x_i ∈ {0,1}, maximize Σx_i subject to all-different pairwise sums. Risk: ~25M constraints for N=10000 may exceed memory. If k_max=105, CP-SAT direction exhausted. **Highest priority.**
2. **VLNS from non-105-mark seeds** (idea_024): Test if self-healing is specific to Bose-Chowla q=107 or universal. E.g., VLNS from Singer q=103 104-mark set targeting 106. Medium priority.
3. **Tabu search with swap-then-fill** (unexplored): research_1 identified as best untried heuristic per literature. Prevents self-healing return by tabu-listing removed elements. Medium priority.

## Coverage Map (grounded in coverage matrix)

**Exhaustively explored (ceilings proven):**
- Bose-Chowla ap q=107: 5+ trials, ceiling 105, self-healing (27K+ perturbation trials)
- VLNS from 105-mark subsets: 85+ trials, all INFEASIBLE at 106
- Singer pp q=103 mul=400: 3 trials, ceiling 104
- Singer pp q=101: 8 trials, ceiling 102
- All greedy variants: 30+ trials, ceiling 70 (beam search k=500+)
- ET(71)+search: 7 trials, ceiling 75; Ruzsa(71)+search: 2 trials, same 75 ceiling
- Singer perturbation all k: 4000+ trials, futile
- CP-SAT k=106 decision: 6000s total, UNKNOWN

**Unexplored:**
- Binary maximize-k CP-SAT: 0 trials
- VLNS from non-105-mark algebraic seeds: 0 trials
- Tabu search (swap-then-fill): 0 trials
- Alternative solvers (Gurobi, SCIP): 0 trials

## Dead Ends

- **Cluster_002** (search-based, exhausted): All greedy/search variants ceiling 66-75. 30-element gap to algebraic. Includes randomized greedy, LNS, SA, beam search, ET extension, Ruzsa-Lindström, backtracking.
- **Cluster_003** (hybrid, exhausted): Singer perturbation, SA from algebraic seed, multi-Singer hybrid — all debunked. 43-blocker minimum makes perturbation structurally impossible.
- **Remove-k perturbation of 105-mark set**: Self-healing property proven for all k (pattern_014). Provably futile.
- **Ruzsa-Lindström as different basin** (idea_025, debunked gen 7): Converges to same 75 ceiling as ET(71). Naive formula invalid in integer arithmetic; only 2p-scaled works (fact_005).

## Open Questions

1. **Is 105 truly F₂(10000)?** Confidence 0.90. CP-SAT returned UNKNOWN, not INFEASIBLE. Binary maximize-k is the last formulation that could settle this. Theoretical gap of 4 to ~109 bound.
2. **Can binary maximize-k CP-SAT even build?** ~25M constraints for N=10000. full_1 interrupted before testing. Memory feasibility unknown.
3. **Is self-healing universal or construction-specific?** VLNS from Singer q=103 (104-mark) targeting 106 untested. If also INFEASIBLE, strengthens F₂=105 claim.
4. **DANGER: Stale fact files persist.** facts/fact_002.md says upper bound "~100-102" (WRONG: ~109). facts/fact_004.md says validator extracts subsets (WRONG: sentinel scoring). 4-generation architectural issue — no orchestrator path updates facts/. Agents reading facts/ will be misled.
5. **Epistemological lesson:** Gen 6 assigned high confidence to wrong VLNS "bug" diagnosis (1 agent). Gen 7 refuted it (3 agents). Critical claims need evidence-source counts, not just confidence numbers.
