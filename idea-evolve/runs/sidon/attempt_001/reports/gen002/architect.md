# Architect Report — Generation 2

## Data Anomalies

- **Three-way tie at 99**: All top-3 solutions are Singer q=97 perturbation variants. No diversity at the frontier. This is unusual — typically you'd expect some score spread. It suggests the 99-element basin is large (many perturbations lead to 99) but the 100-element basin is either very small or nonexistent from this approach.

- **explore_2's invalid solutions**: 2 of 6 solutions had violations (33% invalid rate). Both were 2-opt attempts. This suggests 2-opt from greedy-66 is fragile — element swaps easily break the Sidon property. The blocker analysis in exploit_2 should reveal why.

- **full_1 scored exactly baseline**: The parabola construction attempt was a misfire (312 violations for p=101), and all search methods returned to 66. full_1 essentially contributed zero knowledge beyond "parabola doesn't work." This validates skipping full agents in gen 2.

## Confidence: Medium-High

The plan is well-grounded in gen 1 data. The critical path (exploit_1 on Singer q=101) is mathematically sound and the expected outcome (99-101 elements) is based on probabilistic analysis. The main uncertainty is implementation correctness — GF(101³) arithmetic must be exactly right.

I am less confident in the Track B agents producing competitive scores this generation, but that's by design — their value is in finding new basins, not matching the current best.

## What Didn't Fit

- **Exhaustive k-opt from 99-element set (EXP-6)**: Random k=5-20 removal + refill. Interesting but lower priority than Singer q=101 and SA. Deferred to gen 3 if the barrier holds.

- **Constraint programming / ILP formulation**: Research agent from gen 1 mentioned this. Requires external solvers that may not be available. Low feasibility, deferred.

- **Second Track B explore with a different direction**: Could have assigned one to Ruzsa and one to Bose-Chowla. Budget discipline limited to 5 agents total.

## Strategic Risks

1. **All eggs in Singer q=101**: If exploit_1's implementation is buggy, we lose our highest-priority experiment. No backup agent is implementing q=101. Mitigation: opus model, 1800s timeout, reference code available.

2. **SA from 99-seed might be premature without helpers**: exploit_2 will reimplement SA infrastructure that experimentator_1 is building as helpers. The timing is parallel, so exploit_2 can't use the helpers. This is acceptable — exploit_2's SA is a one-off implementation, and the helpers benefit gen 3+.

3. **Research might not find anything new**: Gen 1 research already found Singer (the breakthrough). Gen 2 research is looking for what's beyond Singer — the pickings may be thinner.

## Open Questions for the System Critic

1. **If Singer q=101 best shift gives exactly 99**: Is this because the Singer set elements cluster near the overflow region {10001..10302}, or is 99 a deeper structural limit? Analyzing the element distribution would help.

2. **Is the 99→100 barrier specific to Singer q=97 perturbation, or does it extend to all Sidon sets of size 99?** If every 99-element Sidon set in {0..10000} is a local maximum (no single-element swap reaches 100), that would be a fundamental result worth documenting.

3. **Should we start tracking explicit element lists (seeds)?** REC-2 and REC-10 both suggest this. If gen 3 agents keep spending 55s re-deriving the 99-element set, the ROI on seed files is clear.
