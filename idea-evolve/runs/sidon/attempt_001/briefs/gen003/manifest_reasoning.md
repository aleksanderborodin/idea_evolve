# Manifest Reasoning — Generation 3

## Situation Assessment

**Score trajectory:** 66 -> 99 -> 102 (strong initial improvement, now plateauing). The 102-element
Singer q=101 set is locally saturated with 40+ blockers per non-member. All Singer primes tested,
all SA/perturbation approaches exhausted. We are stuck at an algebraic ceiling.

**Critical missing information:** Two generations of research agents failed to complete the literature
search for published Sidon set records. We don't know if 102 is competitive or far below the
state of the art. This is the single most decision-critical gap.

**Diversity crisis:** All 10 top solutions score exactly 102, all using Singer q=101. Zero structural
diversity at the frontier. The knowledge base is a gravity well pulling everything toward Singer
refinement, which is provably useless.

## Agent Roster (5 agents)

### research_1 (sonnet, 900s) — Track B: Literature search
**Rationale:** HIGHEST PRIORITY. This is the 3rd attempt at the literature search. The brief is
narrowly scoped: find F(10000) in published tables. No solution code, no analysis — just web search.
If a 105+ element set is published, its construction method immediately becomes our gen 4 strategy.
If 102 is the published best, we know we're at the frontier.

Sonnet is sufficient for web search. 900s timeout matches gen 2 research timing (700s work + buffer).

### exploit_1 (opus, 2400s) — Track A: ILP/constraint programming + large-k perturbation
**Rationale:** The two most promising untested approaches from the coverage matrix. ILP could find
a provably optimal solution if a solver is available. Large-k perturbation (k=10-20) is the only
local-search variant not yet tested. Opus for precision in formulating the ILP constraints correctly.
2400s timeout because gen 2 exploit agents used 1500-1874s and this task is more complex.

### explore_1 (sonnet, 1800s) — Track B: Non-Singer algebraic construction
**Rationale:** Mandatory radical exploration. Directed at correct Bose-Chowla, modular quadratic
residue lifts, or probabilistic constructions. Must NOT use Singer. Even a score of 85 from a
genuinely new algebraic family would be strategically valuable — it opens hybrid possibilities
and validates a new basin.

### explore_2 (sonnet, 1800s) — Track B: Computational search (backtracking/CSP)
**Rationale:** Second mandatory radical exploration, orthogonal to explore_1. Attacks the problem
as a constraint satisfaction problem using backtracking, beam search, or non-SA local search
(tabu, late acceptance). The key insight: SA failed on the Singer set's structure, but a set
found by search may have completely different blocker properties. 1800s because gen 2 explores
used 1200s and this is more compute-intensive.

### experimentator_1 (opus, 1200s) — Track A: Build helpers + Singer gap analysis
**Rationale:** REC-4 requests `find_optimal_shift(q, N)` helper — this is the 2nd consecutive
generation with this recommendation, making experimentator MANDATORY per the recurring helper
rule. Secondary task is EXP-6 (Singer gap analysis) which provides structural understanding
for future exploit strategies. Opus because helper code must be correct.

## What I Deliberately Did NOT Do

1. **No exploit agent for correct Bose-Chowla.** explore_1 covers this direction. Adding an
   exploit would duplicate effort and is premature — we don't have a Bose-Chowla baseline to refine.

2. **No genetic crossover.** All top solutions are identical (Singer q=101). Crossing two copies
   of the same solution is pointless. Genetic agents need diverse parents.

3. **No second exploit agent.** With Singer exhausted, there's only one productive exploit
   direction (ILP/large-k). A second exploit would overlap.

4. **No full agent.** Full agents build end-to-end. Our problem is not "how to build a Sidon set"
   (we have a good one) but "how to exceed a specific algebraic ceiling." This requires targeted
   strategies, not broad end-to-end attempts.

## Timeout Calibration

| Agent | Timeout | Justification |
|-------|---------|---------------|
| research_1 | 900s | Gen 2 research: 700-800s. Literature search is bounded. |
| exploit_1 | 2400s | Gen 2 exploits: 1500-1874s. ILP formulation is more complex. |
| explore_1 | 1800s | Gen 2 explores: 1200-1615s. Algebraic research + implementation. |
| explore_2 | 1800s | Same as explore_1. Backtracking search needs compute time. |
| experimentator_1 | 1200s | Gen 2 experimentator: 434s. Two tasks justifies higher budget. |

## Risks

1. **Literature search fails again.** If research_1 can't find published records in 3 generations,
   we may need to accept the information gap and proceed with heuristic calibration.

2. **No ILP solver available.** exploit_1's primary strategy depends on PuLP or OR-Tools. If
   neither is installable, the agent falls back to large-k perturbation only, which is lower
   probability of success.

3. **Track B agents score <80.** Expected outcome for radical exploration. Not a failure — the
   value is structural diversity and new basins, not immediate score improvement.

4. **Experimentator helper deployment.** The helper won't be available to THIS generation's agents
   (they run in parallel). Its value is for gen 4+.
