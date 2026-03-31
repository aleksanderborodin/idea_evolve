# Manifest Reasoning — Generation 2

## Situation Assessment

**Score trajectory:** 148.18 µs best from gen 1 (5.2x over 770 µs baseline). All 14 solutions follow the same BLIS+AVX-512 template with minor variations.

**Critical change:** Target moved from 477 µs → 24 µs. The old target was already beaten. The new target requires ~6x improvement over current best — this is NOT achievable through incremental refinement of the existing BLIS approach. The user explicitly states "fundamentally new strategies are needed."

**Diversity crisis:** All 14 gen 1 solutions use the same architecture (BLIS tiling, pack A/B, 4×64 micro-kernel). Zero structural diversity. The coverage matrix shows no unexplored high-level approaches — only parameter variations within one architecture.

**Bottleneck analysis (from per-size times):**
- Small (4.49 µs): Already fast. Limited room for improvement.
- Medium (228.26 µs): ~50x slower than small despite only 16x more output. Packing overhead and cache effects dominate. Potential for large improvement.
- Large (3176.31 µs): ~700x slower than small, 32MB output. Likely memory-bandwidth-bound (~1000 µs floor for 32MB DRAM writes). Hardest to improve.
- Geomean = (4.49 × 228.26 × 3176.31)^(1/3) = 148 µs. To reach 24 µs, need all three sizes to improve dramatically, especially medium.

## Agent Mix Rationale

### Track A — Directed Exploitation (1 agent)

**exploit_1 (sonnet, 2700s):** Refines best solution with the top unexplored ideas:
- No-packing direct kernel (idea_013) — highest-priority untested idea, eliminates pack_B overhead
- int8 accumulation — enables wider kernels by halving register pressure
- NC tuning sweep
- Software prefetching

Rationale: Even though incremental refinement won't reach 24 µs, we need to find the floor of the BLIS approach. If no-packing + int8 + wider kernel gets to ~80 µs, that's useful information. If it only gets to ~130 µs, we know the architecture is exhausted.

### Track B — Radical Exploration (2 explores + 1 research)

**explore_1 (sonnet, 2700s):** Row-streaming approach with zero packing, zero tiling. Key insight: k is only 2-7 bytes, so all of A's data for one row fits in 14 registers. Scan B sequentially, compute and store directly. No buffers, no copies, no overhead. This is the simplest possible kernel — if it's competitive, it proves packing was pure overhead.

**explore_2 (sonnet, 2700s):** Three orthogonal non-BLIS approaches:
1. Bit-parallel column processing (invert loop order: k → column → row, process all n rows simultaneously)
2. Per-row lookup tables (precompute 256 results per A byte pair, then just table-lookup for each B column)
3. Register-blocked full-A approach (load all of A into registers, sweep columns)

These are structurally different from anything in gen 1. Even if they don't beat 148 µs, they explore new basins of attraction that might lead to breakthroughs in later generations.

**research_1 (sonnet, 900s):** Theoretical analysis:
- Compute lower bounds (memory bandwidth, compute throughput) for each benchmark size
- Survey production BNN inference engines (BitNet.cpp, XNOR-Net kernels)
- Identify approaches from HPC that apply to tiny-k GEMM
- Port utilization analysis for critical instructions

This answers the crucial question: is 24 µs even theoretically achievable? If the large benchmark has a ~1000 µs memory floor, we need to know.

### Experimentation (1 agent)

**experimentator_1 (opus, 1500s):** Answers the open questions that every gen 1 agent flagged:
1. Per-phase timing breakdown (where does time go in sol10?)
2. Assembly quality inspection (is the compiler leaving performance on the table?)
3. NC sweep across all sizes (systematic data, not guesswork)
4. DRAM bandwidth measurement (what's the physical floor for large benchmark?)

Using opus because this requires careful analysis and correct instrumentation. Results directly inform gen 3 strategy.

## What I Chose NOT To Do

1. **No genetic crossover.** All 14 solutions are structurally identical — crossing them produces more of the same. Genetic is useful when diverse solutions exist.

2. **No full agent.** Full agents do end-to-end implementation. exploit_1 already refines the best, and both explores build from scratch. A full agent would overlap.

3. **No second exploit.** With only one architecture in the population, two exploits would compete for the same optimization space. Better to spend the budget on exploration.

4. **Did not implement REC-6 (research before solution agents).** All agents run in parallel (orchestrator runs them simultaneously). Sequential grouping would delay all agents by research_1's runtime (~8 min) for marginal benefit since the briefs already contain the critical context.

5. **Did not assign REC-8 (score_summary helper).** Low priority compared to the 24 µs target. The evaluator managed fine in gen 1.

## Addressing System Recommendations

| Rec | Status | Action |
|-----|--------|--------|
| REC-1 (write-first cap) | ADDRESSED | All briefs include "write first solution within 10 turns" instruction |
| REC-2 (baseline re-measure) | DEFERRED | experimentator_1 measures bandwidth instead — more useful for 24 µs target |
| REC-3 (vpternlogd convention) | ADDRESSED | exploit_1 brief specifies canonical convention (0xD8/0xE4) |
| REC-4 (perf stat NC) | ADDRESSED | experimentator_1 runs NC sweep with timing |
| REC-5 (no-packing kernel) | ADDRESSED | exploit_1 primary directive + explore_1 uses no-packing by design |
| REC-6 (research first) | NOT IMPLEMENTED | Agents run in parallel; briefs provide context |
| REC-7 (int8 accum) | ADDRESSED | exploit_1 secondary directive |
| REC-8 (score helper) | DEFERRED | Low priority |

## Timeout Rationale

- exploit_1, explore_1, explore_2: 2700s (default). Gen 1 agents needed 1800-2100s. The explore agents have complex implementation work.
- research_1: 900s. Gen 1 research completed in 485s. Research is reading + analysis, not coding.
- experimentator_1: 1500s. Needs to instrument code, compile, run experiments, analyze. More than research but less than solution agents.

## Risks

1. **Both explores fail to produce valid solutions.** AVX-512 intrinsics are error-prone, and these agents are building from scratch without a working template. Mitigation: exploit_1 provides the safety net of improving the known-working approach.

2. **Large benchmark has an unbreakable memory bandwidth floor.** If writing 32MB to DRAM takes ≥1000 µs, then geomean ≥ (1 × 1 × 1000)^(1/3) = 10 µs minimum. But to get geomean = 24 µs with large = 1000 µs, need small × medium = 13.8, i.e., small = 0.5 µs and medium = 28 µs. That's extremely aggressive. experimentator_1 will measure the actual bandwidth to answer this.

3. **No-packing approach is slower due to strided access.** Possible but unlikely — B fits in L2 for all sizes and 2-7 strided rows is minimal TLB pressure. exploit_1 tests this directly.

4. **explore_2's approaches are too exotic to implement correctly in one session.** The lookup table and register-blocked approaches are complex. Mitigation: brief lists three options so the agent can fall back to simpler ones.
