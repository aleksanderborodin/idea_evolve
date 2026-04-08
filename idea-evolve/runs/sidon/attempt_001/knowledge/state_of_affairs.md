---
generation: 6
best_score: 105
trajectory: plateaued
last_updated_gen: 6
---

# State of Affairs — Generation 6

## Current Standing

Best score: **105** (Bose-Chowla affine plane q=107, multiplier=433, span=9884). Achieved gen 5 by experimentator_1, independently confirmed by research_1 and reproduced in gen 6 (exploit_1, full_1). This score has held for 2 generations.
6 generations completed. ~65 solutions evaluated. Trajectory: **plateaued** — no improvement since gen 5.
Theoretical upper bound: **~109** (sqrt(N) + O(N^{1/4}), Carter-Hunter-O'Bryant). Gap: 4 elements.
**Algebraic ceiling: 105** — exhaustive multiplier search over all primes q<=109 and both construction types (Singer pp, Bose-Chowla ap) confirms no 106-mark algebraic set fits in N=10000. The 105-mark set is also **perfectly self-healing**: removing any k elements opens exactly k addable slots, which are always the removed elements (pattern_014, 27K+ trials). Perturbation is provably futile.

## What Works

- **Bose-Chowla ap q=107, mul=433** (idea_022, established, 0.95): 105 elements, span=9884. Pipeline best. Greedy-maximal with zero combinatorial slack.
- **Multiplier optimization** (idea_023, established, 0.9): Essential for all algebraic constructions. Singer q=103 with mul=400 gives 104 (vs 102 with mul=1).
- **Singer pp q=101** (idea_008, established, 0.95): 102 elements. Best Singer-type construction.
- **Rokicki-Dogon database** (idea_020, established, 0.95): Verified source of near-optimal constructions.
- **105 is algebraic ceiling** (pattern_012, confirmed, 0.95): Exhaustive proof.
- **105-mark self-healing** (pattern_014, confirmed, 0.95): Perturbation of any size returns same set. NEW gen 6.
- **All greedy variants ceiling 66-70** (pattern_011/013, confirmed): Beam search k=500+ = 70.
- **ET(71)+1-opt hard ceiling 75** (pattern_015, confirmed, 0.90): 30+ restarts all converge. NEW gen 6.
- **DFS/backtracking = greedy** (idea_005, debunked gen 6): Sequential DFS IS greedy (66).

## Current Frontier

All algebraic constructions and perturbation methods are exhausted. The only path to 106+ is computational search:

1. **VLNS with fixed formulation** (idea_024, active, CRITICAL): Fix abs-equality domain bug ([1,N] -> [0,N]), retry 50+ removal patterns. Each trial is cheap (<1s if infeasible, ~120s if tractable). Current 9 trials all INFEASIBLE due to formulation bug, not genuine infeasibility. **Highest-value next step.**
2. **CP-SAT maximize formulation** (idea_019, active): Instead of decision "find k=106", maximize k. More solver-friendly. Three generations of k=106 decision CP-SAT (6000s total) returned UNKNOWN.
3. **Overnight CP-SAT k=106** (4h+, 16 workers): Previous longest run was 1200s. k=106 is hard even at N=15000, so difficulty is inherent.
4. **F₂(10000) lookup**: OEIS A003022 or `problems/sidon/helpers/rokicki_data.py`. 5 minutes of work that could redirect the entire pipeline. Unanswered for 6 generations due to systemic research agent failure.

## Coverage Map

**Well-explored (ceilings confirmed):**
- Bose-Chowla ap q=107: 2+ trials, ceiling 105 (self-healing, perturbation futile k=1-104)
- Singer pp q=103 + mul=400: 3 trials, ceiling 104
- Singer pp q=101: 8 trials, ceiling 102
- All greedy variants: 30+ trials, ceiling 70 (beam search)
- ET(71)+1-opt: 6 trials, ceiling 75 (hard, 30+ restarts)
- Singer perturbation all k: 4000+ trials, zero improvement
- SA from any seed: 4+ trials, zero improvement
- Remove-k perturbation of 105-mark set (k=1-104): 27K+ trials, perfectly futile
- DFS/backtracking: 1 trial, equals greedy (66)
- CP-SAT k=106 decision: 6000s total compute, UNKNOWN

**Under-explored or untested:**
- VLNS with corrected formulation: 0 valid trials (9 trials had bug)
- CP-SAT maximize formulation: 0 trials
- Alternative solvers (Gurobi, SCIP): 0 trials
- Ruzsa-Lindström construction as SA seed (idea_025): 0 trials
- Tabu search with "swap then fill" moves: 0 trials

## Dead Ends

- **All greedy/search variants** (cluster_002, exhausted): Ceiling 70. 35-element gap to algebraic.
- **All hybrid approaches** (cluster_003, exhausted): Singer perturbation, SA from algebraic seed, multi-Singer hybrid — all debunked.
- **Remove-k perturbation of 105-mark set**: Self-healing property makes this provably futile for all k.
- **DFS/backtracking** (idea_005): DFS IS greedy. Debunked gen 6.

## Open Questions

1. **Can k=106 be achieved for N=10000?** CP-SAT returned UNKNOWN (not INFEASIBLE). VLNS results are artifacts of a formulation bug. Fix VLNS and retry before concluding.
2. **What is F₂(10000)?** Check OEIS A003022 and `problems/sidon/helpers/rokicki_data.py`. This single number determines if 106 is ambitious or already known. Unanswered for 6 generations — systemic research failure.
3. **Is the VLNS formulation genuinely fixable?** The abs-equality domain conflict diagnosis is plausible but untested. Must fix and verify.
4. **DANGER: Stale fact files.** `facts/fact_002` says upper bound "~100-102" (WRONG: ~109). `facts/fact_004` says validator extracts subsets (WRONG: sentinel scoring). Corrected copies exist in `ideas/active/` but originals persist and could mislead agents.
5. **helpers/cpsat.py still missing.** Requested for 3 consecutive generations. Agents re-derive CP-SAT formulation from scratch each time, introducing bugs.
