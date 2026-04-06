# Architect Report — Generation 5

## Data Anomalies

- **Three-generation plateau at 102.** Score has not improved since gen 2. All competitive
  solutions are Singer q=101 variants. This is expected — Singer is exhausted — but the
  lack of progress means the pipeline's entire value now depends on breaking into a new
  score tier. Gen 5 is the most strategically critical generation so far.

- **Rokicki-Dogon claim still unverified after 4 generations.** idea_020 claims 104-105
  mark rulers exist for span<=10000, but no one has downloaded the data. Confidence was
  downgraded from 0.7 to 0.5 in the gen 4 consistency review. If this claim is wrong,
  one of the two credible paths to 103+ collapses.

- **CP-SAT UNKNOWN is ambiguous.** full_1 gen 4 ran k=103 for 600s and got UNKNOWN. This
  is neither evidence for nor against feasibility. The system has been interpreting it as
  "hopeful" but UNKNOWN after 600s is a weak signal — it could equally mean CP-SAT's
  relaxation is too loose to make progress.

- **Stale fact files finally corrected.** The gen 4 consistency review updated fact_002
  and fact_004. This resolves a 3-generation knowledge corruption issue (REC-4 now done).

- **Permission blocking in gen 4 explore_1.** explore_1 was completely wasted due to
  Write/Edit permission denial after the first file write. REC-1 from system critic
  flagged this. If it recurs in gen 5, multiple agent slots could be lost.

- **No exploit or genetic agents in gen 5.** This is a deliberate choice given the
  monoculture at 102 and exhaustion of all refinement approaches. If the pipeline breaks
  through via Rokicki-Dogon or CP-SAT, gen 6 should deploy exploit agents to optimize
  around the new best.

## Confidence: Medium

Higher confidence factors:
- Clear, prioritized action plan aligned with system recommendations
- experimentator_1's task is well-defined and scoped (data fetch, not research)
- full_1 has a known-working formulation to extend
- Beam search is well-specified and independently recommended by multiple agents

Lower confidence factors:
- Rokicki-Dogon data availability is uncertain
- CP-SAT may hit a compute wall at k=103
- Track B explore_2 is genuinely speculative
- F(10000) may be impossible to find online (4 prior failures)

## What Didn't Fit

- **CP-SAT helper creation (REC-6).** Important for gen 6+ but not worth a slot when
  full_1 is already running CP-SAT directly. Deferred to gen 6 if CP-SAT remains viable.

- **Singer-102 JSON seed (REC-9).** 3rd generation without implementation. Low impact —
  agents can extract the set from existing solution files. Not worth an agent slot.

- **Stochastic min-blocking (EXP-F).** Lower priority than beam search. If beam search
  works, stochastic methods are superseded. If beam search fails, stochastic will too.

- **Alternative solver testing (EXP-E).** Would be valuable if we had more slots. The
  information gain (is CP-SAT the bottleneck or the problem?) is useful but not urgent.

## Strategic Risks

1. **Generation 5 produces zero improvement.** If Rokicki-Dogon fails, CP-SAT remains
   UNKNOWN, beam search ceilings at 72, and Track B scores below 60 — we've spent 5
   agents with no score improvement for 4 consecutive generations. This would suggest
   the problem requires compute resources (longer solver runs, commercial solvers) or
   approaches (distributed search) beyond what individual agent sessions can provide.

2. **Rokicki-Dogon success creates false satisfaction.** If experimentator_1 finds a
   105-element set from the database, the pipeline may stop pushing. But 105 is still
   4 below the upper bound of 109. The CP-SAT and research directions remain critical
   even after a Rokicki-Dogon success.

3. **Beam search runtime explosion.** k_beams=100 at N=10000 might require hours.
   explore_1 may only get results for k_beams<=20, which might not be enough to
   escape the greedy basin.

## Open Questions for the System Critic

1. Should the pipeline invest in installing alternative solvers (HiGHS, SCIP) for
   gen 6? This requires a one-time experimentator session for setup.

2. Is there a way to run CP-SAT outside normal agent sessions (e.g., background
   process with 4-hour budget)? The 2700s session timeout may be fundamentally
   insufficient for ILP at this scale.

3. If Rokicki-Dogon fails, what is the next highest-priority exact construction
   method? The pipeline may be running out of low-hanging fruit.
