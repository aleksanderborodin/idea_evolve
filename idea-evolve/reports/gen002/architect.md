# Architect Report — Generation 2

## Data Anomalies

1. **Zero structural diversity.** All 14 gen 1 solutions follow identical BLIS architecture. The coverage matrix shows parameter variation (NC values, accumulator widths) but zero algorithmic diversity. This is a red flag — the system explored one basin of attraction thoroughly but never left it.

2. **explore_2 total failure.** Spent entire session reading files, produced 0 solutions. 25% of gen 1 agent capacity wasted. All briefs now include explicit "write first within 10 turns" instruction.

3. **Target change is radical.** 477 µs → 24 µs is a 20x harder target. The old target was 62% of baseline; the new one is 3%. Every gen 1 solution is now inadequate, not just suboptimal. The entire knowledge base's "what works" assessment is relative to a much easier goal.

4. **Per-size time distribution is highly skewed.** small=4.5, medium=228, large=3176. The large benchmark dominates the geomean but may have a physical floor (~1000 µs for 32MB DRAM writes). This could make 24 µs impossible if the scoring is geometric mean. experimentator_1 will measure the actual bandwidth ceiling.

## Confidence: Medium

The plan is sound in structure (1 exploit refining known-good, 2 radical explores, 1 research, 1 experimentator). But I have medium confidence because:

- The 24 µs target may be physically impossible depending on DRAM bandwidth for the large benchmark. We don't have the data yet to know.
- Both Track B explores are building from scratch without a working template — high risk of correctness failures.
- The gen 1 knowledge base optimized for 477 µs, not 24 µs. Strategies that were "good enough" (skip memset, deferred widening) are now table stakes, not differentiators.

## What Didn't Fit

- **perf stat profiling for NC regression (REC-4):** experimentator_1 does NC sweep but not hardware counter profiling. Would need `perf stat` which may not be available in the sandbox. Deferred to a future experimentator if timing data from Exp 1 suggests NC is a bottleneck.
- **vpternlogd canonical verification (EXP-6):** Both conventions work. Lower priority than the 24 µs target work. The exploit brief specifies which convention to use.
- **Second research agent on memory optimization techniques.** Could be valuable but budget-constrained (5 agents already).

## Strategic Risks

1. **Bandwidth ceiling makes target impossible.** If geomean scoring means (small × medium × large)^(1/3) and large has a ~1000 µs floor, then 24 µs requires small≈0.5 and medium≈28. That's ~10x improvement on small (from 4.5) and ~8x on medium (from 228). Possible but aggressive.

2. **All explores produce invalid solutions.** Building AVX-512 kernels from scratch is hard. If both Track B explores fail, we learn nothing about alternative architectures and gen 3 is no better informed than gen 2.

3. **Exploit hits diminishing returns quickly.** If no-packing + int8 only improves to ~120 µs, the BLIS architecture is confirmed as capped and we're fully dependent on Track B for breakthroughs.

4. **Research finds 24 µs is infeasible.** If the theoretical analysis shows the target exceeds hardware limits, we need to communicate this to the user and negotiate a realistic target.

## Open Questions for the System Critic

1. **Is the scoring metric geometric mean or true median (middle value)?** The user intervention says "geometric median" and scoring changed from mean to median. For 3 values, if it's the true median (middle sorted value), then medium benchmark alone determines the score — large doesn't matter. This fundamentally changes strategy. Please verify with the actual evaluation code.

2. **What is the achievable DRAM write bandwidth on this machine?** experimentator_1 will measure this, but the System Critic should flag if the 24 µs target is physically impossible given the large benchmark's 32MB output.

3. **Should we propose a target revision?** If theoretical analysis shows 24 µs is beyond hardware limits, the System Critic should recommend a realistic target to the user.
