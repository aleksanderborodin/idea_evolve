# Manifest Reasoning — Generation 5

## Situation Assessment

**Score: 102 (plateaued 3 generations).** Singer q=101 truncation is the ceiling for all
Singer-based and greedy-based approaches. The pipeline has exhaustively confirmed:
- Singer perturbation: futile (43+ blockers per non-member)
- Multi-Singer hybrid: debunked (zero compatible elements)
- All greedy variants: ceiling 66-69
- SA from any seed: zero improvement
- Ruzsa/CRT constructions: violate Sidon property in integers

**Two credible paths to 103+:**
1. Rokicki-Dogon database (idea_020): May contain 104-105 mark sets for span<=10000.
   Unverified after 4 generations. This is a pure data-fetch task.
2. CP-SAT ILP (idea_019): k=103 returned UNKNOWN (not INFEASIBLE) after 600s.
   Needs longer runs. Singer proven suboptimal at small N.

**One high-potential untested direction:**
- Beam search greedy: flagged by 4+ agents across gens 3-4, expected 75-85, never implemented.

## Agent Mix Rationale (5 agents)

### Track A — Directed exploitation (3 agents)

**experimentator_1 (opus, 1200s):** Rokicki-Dogon data fetch. This is the single highest-ROI
action — if 104-105 mark rulers exist for span<=10000, we jump from 102 to 104-105 in one
session. Using opus because data parsing can be tricky and this is mission-critical. Four
generations have approached this without completing. Using experimentator (not research)
because this is a data engineering task, not a literature search.

**full_1 (sonnet, 2700s):** CP-SAT dual mission. Part A: Singer+1 structure analysis at
small N (EXP-D) — understand WHY ILP finds larger-than-Singer sets. Part B: extended CP-SAT
run for k=103 at N=10000 with maximum available time. Using the maximum timeout (2700s)
because gen 4's full_1 hit timeout at 1800s and CP-SAT benefits from more wall clock time.
Using sonnet (not opus) because the formulation is already known — this is execution, not
discovery.

**explore_1 (sonnet, 1500s):** Beam search greedy. This bridges the gap between greedy (69)
and algebraic (102). If beam search reaches 80+, it validates that the greedy ceiling is a
one-beam artifact and opens a new optimization frontier. If it also ceilings at 69-72, that's
equally valuable — it confirms the structural limit and saves future agents from trying.
Higher timeout because beam search with large k can be compute-intensive.

### Track B — Radical exploration (2 agents, mandatory)

**explore_2 (sonnet, 1200s):** Radical exploration from scratch. Explicitly forbidden from
using Singer, greedy, SA, or any current technique. Given four orthogonal options:
backtracking with pruning, probabilistic alteration, graph-based independent set, or
number-theoretic sieving. Any score from a genuinely new approach is valuable — even 80
from a new basin is more strategically important than another 102 from Singer.

**research_1 (sonnet, 1200s):** Literature deep dive. Primary mission: find published
F(10000) — this has been an open question for 4 generations and determines whether 102 is
near-optimal or far below. Secondary: find construction methods the pipeline has never tried
(Bose-Chowla correct version, Cilleruelo, Lindström). Brief enforces incremental writing
to prevent the loss-on-timeout pattern that killed gen 2-3 research.

## What I Deliberately Chose NOT To Do

1. **No exploit agent.** There is nothing productive to exploit — the 102 ceiling from Singer
   is proven impenetrable by perturbation, SA, hybrid, or any local modification. An exploit
   agent would waste a slot re-confirming this.

2. **No genetic crossover.** The top 3 solutions are all Singer q=101 variants (identical
   elements). Crossing identical parents produces identical offspring. The only meaningful
   crossover would be Singer x ET(71), but that's essentially what the debunked hybrid
   approach was. Not worth a slot.

3. **No experimentator for CP-SAT helper (REC-6).** full_1 will be implementing CP-SAT
   directly, and the formulation is already documented in idea_019. Creating a helper is
   lower priority than using the actual session time for solving. If full_1 succeeds in
   finding k=103, the helper becomes less critical. If it fails, gen 6 should create the
   helper for future attempts.

4. **No stochastic min-blocking (EXP-F).** Lower priority than beam search. If beam search
   confirms the greedy ceiling is structural, stochastic min-blocking would also fail.
   If beam search succeeds, stochastic methods become less interesting.

5. **No alternative solver testing (EXP-E).** Requires installing additional packages
   (highspy, pyscipopt) which may not be available. CP-SAT is the known-working solver.
   Spending time on solver comparison is less valuable than running CP-SAT longer.

## Timeout Calibration

Based on gen 4 timing data:
- experimentator_1 gen 4: 475s → 1200s (generous for download + parsing)
- full_1 gen 4: 1887s (hit 1800s timeout) → 2700s (maximum, CP-SAT needs all available time)
- explore_1: 1500s (beam search is compute-heavy, more than standard explore)
- explore_2: 1200s (standard explore budget, sufficient for construction + evaluation)
- research_1 gen 4: 1320s (hit timeout) → 1200s (incremental writing should help)

## Risks

1. **Rokicki-Dogon download may fail.** Server could be down, zip format could be unusual,
   or 104-105 mark rulers may not exist for span<=10000. Experimentator_1 has a fallback
   (Singer q=103 span reduction), but if the database claim is wrong, idea_020 collapses.

2. **CP-SAT may remain UNKNOWN.** Even with 2700s, k=103 at N=10000 may be beyond CP-SAT's
   capability. The problem may require commercial solvers or days of compute. If UNKNOWN
   persists, we need to consider whether this direction has a compute wall.

3. **Beam search may be too slow.** With k_beams=100 and N=10000, the search tree is enormous.
   Memory and time may limit practical beam widths to 20-50, which might not be enough to
   escape the greedy basin.

4. **Track B explore may produce only low scores.** Radical approaches often score poorly
   initially. The value is in discovering new basins, not immediate high scores. But if
   explore_2 scores below 50, the new approach may not be worth pursuing further.

5. **Research_1 may again fail to find F(10000).** This has been an unsolved problem for
   4 generations. The value may simply not be published for N=10000 specifically.
