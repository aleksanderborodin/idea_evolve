# Manifest Reasoning — Generation 3

## Situation Assessment

**Score trajectory:** 148.18 µs (gen 1) → 147.26 µs (gen 2) — effectively flat. Gen 2 improvement was 0.6%, within measurement noise. The system has plateaued at ~147 µs.

**Critical resolution:** The scoring metric is confirmed as **geometric mean** of 3 per-size median times: `(small × medium × large)^(1/3)`. This was the #1 open question flagged by 4 agents across gen 2. All three sizes matter equally in the geomean. Large-benchmark optimization (NT stores) is strategically valid.

**Key gen-2 findings:**
- BLIS architecture is exhausted: 12 exploit variants all regressed (pattern_007)
- Row-streaming architecture matched BLIS best (147.26 µs) with simpler code
- NT stores give 2.3x on large but C alignment blocks direct use (fact_006)
- Int8 accumulation gives 11-13% kernel improvement (experimentator_1)
- 8-row int8 kernel is theoretically sound but never built (idea_016)
- vpshufb LUT kernel never tested (idea_018)
- Port 5 bottleneck identified but fact_004 port assignments are disputed

**Consistency review failed in gen 2** — state_of_affairs.md is stale (still says generation 1). Gen 3 evaluator + consistency reviewer (every 3rd gen) will update it.

**Physics floor analysis:** research_1 calculated geomean(0.5, 80, 640) ≈ 29 µs with aggressive assumptions (NT stores + near-zero small + near-bandwidth-floor medium). The 24 µs target is ambitious but potentially reachable with fundamentally better approaches.

## Agent Mix Rationale

**5 agents (2 Track A, 2 Track B, 1 measurement):**

### Track A — Directed exploitation

1. **exploit_1 (opus, 2700s):** Highest-ROI agent. Starts from row-streaming best (sol01, 147.26 µs) and incrementally adds:
   - Phase 1: Aligned-buffer NT stores for large (expected: ~80-110 µs geomean)
   - Phase 2: 8-row int8 kernel (expected: additional 11-13%)
   - Phase 3: Combine both (expected: 60-90 µs geomean)

   Uses opus because precision matters for AVX-512 correctness. 2700s timeout because gen-2 exploit used 2011s and this has more phases.

2. **explore_1 (opus, 2700s):** Full-stack from-scratch attempt combining all three major optimizations simultaneously (idea_014 + idea_015 + idea_016). Different approach angle from exploit_1: builds clean rather than incrementing. If exploit_1's incremental approach misses a synergy, this agent may find it. Uses opus for the same correctness reasons.

### Track B — Radical exploration

3. **explore_2 (sonnet, 2700s):** vpshufb nibble-LUT kernel — a completely different compute path that eliminates the ternarylogic+popcount approach entirely. Addresses port 5 bottleneck (pattern_008). Even if slower, this produces critical information about whether port 5 is actually the binding constraint. Sonnet because the approach is well-specified and doesn't need opus-level reasoning.

4. **research_1 (sonnet, 900s):** Investigates approaches the system has never tried:
   - How to push small below 1 µs (pack-free, 32-row simultaneous)
   - Alternative output strategies for large (compressed, int16, mmap)
   - VNNI repacking (revisiting debunked idea_003 with fresh angle)
   - Production BNN inference kernel techniques (daBNN, BMXNet)
   - Tiger Lake IPC and micro-op fusion opportunities

   900s timeout — gen-2 research took 900s work + 216s wrap-up. Pure research, no code to write.

### Measurement

5. **experimentator_1 (sonnet, 1200s):** Three targeted experiments:
   - Aligned-buffer + memcpy end-to-end overhead (validates exploit_1's Phase 1 premise)
   - fact_004 port assignment verification (resolves 2-generation dispute)
   - Small benchmark pack-free measurement (quantifies small-size optimization potential)

   Results feed gen 4 (parallel execution means gen 3 agents can't use them). 1200s is generous — gen-2 experimentator used 1500s for more complex experiments.

## What I Deliberately Chose NOT to Do

- **No genetic crossover.** The population has only two architectures (BLIS and row-streaming), both using the same core compute (ternarylogic+popcount). Crossing them would produce something in between, not something new. Genetic agents are better used when there are 3+ diverse high-scoring solutions.

- **No second exploit refining BLIS.** BLIS is exhausted (12/12 variants regressed). Any exploit starting from BLIS is wasted compute.

- **No experimentator for helper creation.** system_recommendations.md doesn't flag recurring helper needs. The score_summary helper (gen-1 REC-8) is low priority.

- **No more than 5 agents.** Budget discipline. Each additional agent costs $2-5 (opus) or $0.50-1 (sonnet). Five agents provide sufficient parallelism and diversity.

## Timeout Justification

| Agent | Timeout | Gen-2 Reference | Rationale |
|-------|---------|-----------------|-----------|
| exploit_1 | 2700s | exploit_1: 2011s | More phases, needs full time |
| explore_1 | 2700s | explore_1: 2867s (with wrap-up) | Full-stack is complex, match gen-2 |
| explore_2 | 2700s | explore_2: 2935s (with wrap-up) | New approach from scratch, similar complexity |
| experimentator_1 | 1200s | experimentator_1: 1743s | Simpler experiments this gen |
| research_1 | 900s | research_1: 1116s (with wrap-up) | Pure research, no code |

## Risks

1. **Both Track A agents fail on correctness.** AVX-512 NT stores + int8 accumulation + 8-row kernels are complex. If both exploit_1 and explore_1 produce only invalid solutions, gen 3 makes no score progress.

2. **vpshufb LUT is fundamentally slower.** The 2 vpshufb + nibble extraction per k-byte may exceed the 5-instruction popcount path in total throughput, even if port 5 is relieved. If so, we confirm port 5 isn't the bottleneck but have no new compute approach.

3. **Aligned-buffer memcpy erases NT store benefit.** If the memcpy is slower than expected (e.g., due to page faults on the aligned buffer), the net benefit on large is minimal. exploit_1 should test incrementally and abandon if Phase 1 doesn't improve score.

4. **Medium benchmark is near its floor.** At 225 µs with ~80 µs being the physics minimum, there's only ~3x headroom. If medium can't be improved significantly, the geomean is bounded.
