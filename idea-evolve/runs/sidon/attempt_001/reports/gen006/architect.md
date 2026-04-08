# Architect Report — Generation 6

## Data Anomalies

- **105-mark set is greedy-maximal AND perturbation-resistant (k=1,2).** This is unusual for
  a combinatorial object — most locally optimal solutions have small-perturbation neighbors.
  The 4000 trials at k=1,2 with zero improvement suggests the 105-mark basin may be deeply
  isolated. If k=3-10 also fails, the entire perturbation paradigm is questionable.

- **CP-SAT has consumed ~3600s across 5 runs with zero signal.** UNKNOWN is not evidence of
  infeasibility, but 5 consecutive UNKNOWN results at different k values and hint strategies
  is a pattern. The solver may be fundamentally unsuited to this constraint structure.

- **Gen 5 small-N analysis is alarming.** Optimal sets share 1/12 elements with Singer at
  q=11. If this generalizes, warm-starting CP-SAT from the 105-mark set may be no better
  than warm-starting from nothing. We're assuming the 105-mark set is "close" to optimal
  for k=106, but the small-N evidence suggests otherwise.

- **idea_005 has been stale for 5 generations.** This is a process failure — the pipeline
  kept flagging it without acting. Assigning it to explore_1 this generation resolves it.

- **Duplicate work in gen 5.** Both experimentator_1 and research_1 downloaded the Rokicki-Dogon
  database independently (~2000s wasted). Fixed in this gen: single ownership per task.

## Confidence: Medium

Higher confidence:
- exploit_1's task is well-defined and high-value (remove-k, k=3-10)
- experimentator_1's helper creation is straightforward and addresses a real pain point
- research_1 has a focused mission with clear deliverables
- All system recommendations (REC-1 through REC-10) are addressed

Lower confidence:
- CP-SAT's track record is poor — gen 6 may produce another UNKNOWN
- Backtracking at N=10000 may be impractically slow
- The 105-mark set may be an isolated local optimum with no nearby 106-element sets
- F₂(10000) may still be unfindable

## What Didn't Fit

- **Second CP-SAT run with different formulation** (binary IP instead of integer variables).
  full_1 will try HiGHS with this formulation, but a dedicated agent for formulation
  comparison would be higher quality. Deferred.

- **Anti-algebraic CP-SAT** (forbid all 105 known elements, search for a completely different
  106-element set). High information value but no agent capacity.

- **Adaptive perturbation** (learn which removals are promising and bias sampling). More
  sophisticated than random removal but requires more implementation time than exploit_1 has.

- **Experimentator for Bose-Chowla formula clarification** (REC-3). The knowledge base
  has ambiguous documentation about the correct vs. incorrect Bose-Chowla formula. This is
  a knowledge hygiene issue, not a solution-finding issue. Deferred to evaluator.

## Strategic Risks

1. **We may be at the true optimum.** If F₂(10000) = 105, all computational search is wasted.
   The theoretical upper bound (~109-114) is not tight — the actual maximum could be anywhere
   in [105, 114]. research_1's literature search may narrow this.

2. **Compute allocation may be wrong.** exploit_1 (perturbation) vs full_1 (CP-SAT) is a
   50/50 bet. If one paradigm is fundamentally wrong, half the compute is wasted. But we
   can't know which without trying both.

3. **Track B may produce nothing actionable.** Backtracking might just confirm greedy ceiling
   (70) and research might fail to find novel methods. This is acceptable — Track B's purpose
   is insurance against incrementalism, not guaranteed improvement.

## Open Questions for System Critic

1. Should we escalate CP-SAT to a dedicated 4h+ run in gen 7 if gen 6 is still UNKNOWN?
   At what point do we abandon CP-SAT entirely?

2. If remove-k perturbation fails for all k up to 10 on the 105-mark set, what computational
   approaches remain? Is the problem effectively solved at 105?

3. The small-N analysis showing optimal ≠ Singer needs validation at larger N. Should gen 7
   include a dedicated experiment: run CP-SAT at N=500-2000 (where it can find optimal) and
   measure optimal-vs-algebraic overlap as a function of N?

4. Are there any published computational records for Golomb rulers / Sidon sets at exactly
   N=10000 that we're missing? The pipeline has tried and failed 4 times to find this data.
