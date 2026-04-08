# Manifest Reasoning — Generation 6

## Situation Assessment

**Score: 105** (Bose-Chowla ap q=107, mul=433). Up from 102 plateau (gens 2-4). The gen 5
breakthrough came from the Rokicki-Dogon database — not from any search method the pipeline
developed. The algebraic ceiling is exhaustively confirmed at 105 (every prime q≤109, both
construction types, all multipliers searched). Target: ~109.

**Trajectory: improving but hitting a wall.** The 102→105 jump was a knowledge breakthrough
(discovering the right database), not a computational one. The remaining gap (105→109) requires
genuine computational search — finding sets that no algebraic construction produces.

**Key facts from gen 5:**
- 105-mark set is greedy-maximal (zero addable elements)
- k=1,2 perturbation: 4000 trials, zero improvement
- CP-SAT: 5 runs totaling ~3600s, all UNKNOWN for k=103-106
- Beam search: ceiling 70 (closed greedy direction)
- Small-N analysis: optimal Sidon sets share almost nothing with Singer/algebraic constructions
- idea_005 (backtracking): never tested in 5 generations

## Agent Mix Rationale (5 agents)

### Track A — Directed exploitation (3 agents)

**exploit_1 (opus, 2700s): Remove-k perturbation k=2-10**
- Rationale: This is the single most promising unexplored computational path. k=1,2 failed
  (4000 trials) but k=3-10 is a qualitatively different search — removing 3+ elements opens
  dramatically more room for greedy re-extension. With millions of trials and opus-level
  implementation quality, this has the best chance of finding 106.
- Why opus: The implementation needs to be FAST (inner loop called millions of times). Opus
  is more likely to write an efficient C-like inner loop with proper set operations.
- Why 2700s: Needs maximum compute time for trial volume.

**full_1 (sonnet, 2700s): CP-SAT k=106 + HiGHS + N binary search**
- Rationale: CP-SAT is the only proven approach for finding sets beyond algebraic constructions,
  but it has failed 5 times at ≤600s per phase. This session gives it a single 1200s run
  (2x longest previous) with the 105-mark hint instead of Singer. Also tests HiGHS as an
  alternative solver — different LP relaxation strategy may succeed where CP-SAT fails.
  N binary search reveals whether k=106 is even geometrically feasible at N=10000.
- Why sonnet: CP-SAT/HiGHS formulation is straightforward code. No need for opus.
- Why 2700s: Solver runs are inherently long.

**experimentator_1 (sonnet, 900s): Create shared helpers**
- Rationale: MANDATORY per recurring helper recommendation (REC-5 + REC-6, unresolved 2+
  consecutive generations). Creates `helpers/rokicki_data.py` (static data) and
  `helpers/extend.py` (greedy_extend, perturbation utilities). These save 10+ turns per
  agent in future generations.
- Why sonnet: Helper creation is mechanical — extract data, implement well-defined functions.
- Why 900s: Simple task, should complete in 15-20 minutes.

### Track B — Radical exploration (2 agents)

**explore_1 (sonnet, 1500s): Backtracking/DFS from scratch (idea_005)**
- Rationale: Resolves the 5-generation-stale idea_005. Backtracking with constraint propagation
  is a genuinely different paradigm from greedy/algebraic/perturbation. Even if it only reaches
  70 (confirming the structural ceiling), that's high-value information. If it exceeds 70,
  we've found a new search basin.
- Why Track B: Starts from scratch, not from the 105-mark set. Tests whether exhaustive search
  can exceed greedy methods, independent of algebraic constructions.
- Why 1500s: Backtracking needs time to explore the search tree.

**research_1 (sonnet, 900s): Literature search for F₂(10000) and novel methods**
- Rationale: Open question #2 (exact F₂(10000) record) has been unanswered for 4 generations.
  Knowing the exact target changes the entire strategy. Also searches for construction methods
  the pipeline has never tried (Cilleruelo, Ruzsa-Lindström, SAT encoding, tabu search).
- Why Track B: Looking for ideas the system has never tried, from outside the current
  knowledge gravity well.
- Why 900s: Literature search is fast.

## What I Chose NOT to Do

1. **No genetic crossover.** The top solutions are all algebraic variants (105, 104, 102) with
   no meaningful diversity to cross. Genetic crossover between near-identical sets is wasteful.

2. **No second explore.** One Track B explore (backtracking) is sufficient. A second explore
   would likely be assigned another greedy variant, which is a closed direction.

3. **No CP-SAT helper module.** full_1 already implements CP-SAT inline. Creating a reusable
   helper is lower priority than rokicki_data and extend helpers. Deferred to gen 7 if CP-SAT
   shows progress.

4. **No anti-algebraic CP-SAT** (forbidding known construction elements). This is interesting
   but full_1 already has enough to do. If CP-SAT makes any progress in gen 6, assign this
   variant in gen 7.

5. **No exploit on the 104-mark set.** The 105-mark set is strictly better. All perturbation
   effort should focus on 105.

## Timeout Rationale

Based on gen 5 timing:
- exploit_1: 2700s — opus agent doing heavy compute (millions of trials). Gen 5 full_1 used
  2700s + 736s wrap-up. This needs similar budget.
- full_1: 2700s — CP-SAT/HiGHS runs are inherently long. Gen 5 full_1 needed full budget.
- experimentator_1: 900s — simple helper creation. Gen 5 experimentator took 698s.
- explore_1: 1500s — backtracking needs time. Gen 5 explore_1 took 1691s (1500s + wrap-up).
- research_1: 900s — literature search. Gen 5 research_1 took 1431s (1200s + 230s wrap-up).
  900s should suffice for a more focused mission.

## Risks

1. **Remove-k perturbation may be structurally futile.** If the 105-mark set sits in an
   isolated basin with no 106-element neighbors reachable by k-swap, all perturbation effort
   is wasted. But we can't know without trying k≥3.

2. **CP-SAT may never resolve k=106.** After ~5000s total of UNKNOWN results, CP-SAT may
   simply be the wrong tool. HiGHS is our hedge. If both fail, we need to seriously consider
   whether k=106 is achievable at N=10000.

3. **Backtracking is likely too slow for N=10000.** DFS on a space of 10001 positions is
   enormous. Constraint propagation helps but may not enough. This is an accepted risk for
   Track B — the goal is information, not score improvement.

4. **F₂(10000) may not be publicly available.** Four prior attempts failed to find it. If
   it's not tabulated anywhere, we're stuck estimating from the ~109-114 upper bound range.
