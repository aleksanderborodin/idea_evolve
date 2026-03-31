# Architect Report — Generation 1

## Data Anomalies
None — this is a cold start with no prior data to be anomalous.

## Confidence: High

The plan is straightforward for a cold start. The problem has a clear optimization axis
(AVX2 → AVX-512), the target CPU's capabilities are well-documented, and the baseline
implementation is readable and well-structured. The initial ideas are concrete and actionable.

The two explore agents have genuinely orthogonal directions (popcount+unroll vs VNNI+wide-µkernel).
The full agent provides a belt-and-suspenders integration attempt. The research agent will
surface ideas we haven't considered.

## What Didn't Fit

- **Prefetching experiments:** Software prefetching (`_mm_prefetch`) could help the large
  benchmark but needs empirical testing. Didn't have agent capacity for a dedicated
  prefetching study — research_1 will survey the literature on this.
- **Pack routine optimization:** SIMD-accelerated packing could help but is secondary to
  the micro-kernel improvements. full_1 is briefed to try it but it's not the primary focus.
- **vpternlogd exploration:** This AVX-512 instruction can compute any 3-input boolean
  function in one instruction, potentially reducing the pos/neg contribution calculation.
  Assigned to research_1 for theoretical analysis.

## Strategic Risks

1. **All agents produce incorrect solutions:** AVX-512 intrinsics are error-prone. If all
   4 agents spend their turns debugging and never produce valid solutions, gen 1 yields
   zero usable code. Mitigation: full_1 starts from the working baseline structure and
   upgrades incrementally.
2. **Benchmark variance masks real improvements:** The per-size times can fluctuate with
   system load even on pinned cores. Small improvements (<5%) may be noise. Agents should
   look at the detail_file for per-size consistency.
3. **Memory bandwidth ceiling on large benchmark:** The large benchmark (128×65536, 32MB output)
   may be fundamentally memory-bound. No amount of compute optimization will help if we're
   saturating memory bandwidth. research_1 should investigate this.

## Open Questions for the System Critic

1. Is the V14opt baseline score of ~770 µs reproducible, or does it vary significantly
   between runs? Evaluation variance would affect how we interpret improvements.
2. For the large benchmark (m=65536), what fraction of time is spent in the micro-kernel
   vs packing vs loop overhead? This determines where optimization effort is best spent.
