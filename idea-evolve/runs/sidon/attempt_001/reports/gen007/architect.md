# Architect Report — Generation 7

## Data Anomalies

- **Self-healing property is remarkable and suspicious.** The 105-mark set has a structural
  invariant: removing ANY k elements (k=1 to 104) opens exactly k addable slots, which are
  always the removed elements themselves (pattern_014, 27K+ trials). This is extremely unusual
  for a combinatorial object. It suggests the set may be uniquely optimal — or at least
  uniquely rigid — in its local neighborhood. If true, VLNS (which fixes most elements and
  searches nearby) may be fundamentally limited for this specific set.

- **CP-SAT k=104 returned UNKNOWN in 30s with full hint.** This is alarming. k=104 is BELOW
  the known best — the solver should trivially find 104 elements from the 105-mark hint by
  dropping one element. The fact that it returned UNKNOWN suggests the AllDifferent formulation
  is so hard that CP-SAT cannot even verify sub-optimal solutions quickly. This strongly
  supports switching to binary variable formulation (REC-5).

- **F₂(10000) unknown after 6 generations is a process failure, not a knowledge gap.**
  Every research agent has been briefed to look this up. Every one has failed — sessions
  terminated early, wrote from training data, or drifted into literature review. The gen 7
  brief has mandatory ordered steps and source labeling to force compliance. If research_1
  still fails to perform web searches, there is a systemic issue with the research agent
  template or tool availability.

- **The gen 6 consistency review found 11 files needing updates and 2 critically wrong facts.**
  fact_002 said upper bound "~100-102" (should be ~109) and fact_004 said validator extracts
  subsets (should be sentinel scoring). These have been wrong since gen 0 and corrected copies
  existed in ideas/active/ since gen 2 — but the originals persisted. This is a 4-generation
  data integrity failure.

- **Duplicate work pattern persists.** exploit_1 and experimentator_1 both implement VLNS
  this generation. I accepted this overlap because they serve different purposes (experiment
  vs. reusable tool), and running them in parallel is more valuable than serializing. But
  if both succeed, the next Architect should consolidate.

## Confidence: Medium-High

**Higher confidence:**
- experimentator_1's task is well-scoped and addresses a validated 3-generation pain point
- exploit_1's VLNS fix is a 2-line change with clear diagnosis from gen 6
- research_1 has mandatory steps that should prevent the training-data-only failure pattern
- No wasted agents — every agent addresses a top-priority recommendation or mandatory Track B

**Lower confidence:**
- Binary variable CP-SAT (full_1) may hit model size limits — 25M forbidden tuples is a lot
- VLNS fix may not resolve the bug (diagnosis is plausible but untested)
- Ruzsa-Lindström (explore_1) likely achieves 70-75, well below frontier — value is in the
  new basin, not the absolute score
- F₂(10000) may genuinely not be published anywhere accessible via web search

## What Didn't Fit

- **Second Track B explore** with tabu search or GRASP. Research_1 gen 6 identified these
  from training data. Would need a research finding to validate before implementation.
- **Commercial solver trial (Gurobi, SCIP).** Neither is likely installed. Would need an
  experimentator to set up, eating an agent slot for infrastructure.
- **Swap graph full enumeration (EXP-8).** Low priority — self-healing property already
  suggests uniqueness. Deferred.
- **SA from 75-element ET seed (EXP-7).** Interesting but likely capped at 80. Explore_1
  is doing Ruzsa-Lindström instead, which is more orthogonal.

## Strategic Risks

1. **We may be at the true optimum.** If F₂(10000) = 105, all three Track A agents produce
   zero improvement. The pipeline's remaining value would be confirming optimality and
   documenting the search, not finding better solutions.
2. **Binary CP-SAT may be infeasible to even build.** With N=10000, the number of forbidden
   4-tuples is enormous. full_1 may spend the entire session building the model and never
   reach solver execution.
3. **Research_1 may fail AGAIN.** If web searches return no useful results and rokicki_data.py
   doesn't contain F₂(10000), we'll be at gen 8 with the same open question. At that point,
   I would recommend the user manually check OEIS A003022.
4. **Ruzsa-Lindström may produce sets equivalent to Singer/Bose-Chowla.** Different
   construction formulas can produce identical or near-identical sets. explore_1 should
   verify distinctness, but may not think to do so.

## Open Questions for the System Critic

1. **Should we set a "give up" threshold?** If gen 7 produces no improvement and F₂(10000)
   is confirmed as 105, the pipeline has reached its limit. Define exit criteria.
2. **Is there a systemic issue with research agent web search capability?** 6 consecutive
   generations of failure suggests the tool may not work as expected in --print mode.
3. **Should stale fact files be deleted or just overwritten?** The consistency review
   produced corrected versions, but the originals in facts/ may not have been replaced.
   Verify the state of fact_002.md and fact_004.md in facts/.
4. **Are pattern files in ideas/ causing evaluator confusion?** pattern_009.md in
   ideas/active/ and pattern_011.md in ideas/confirmed/ are misplaced. The evaluator's
   knowledge dump may include them incorrectly.
