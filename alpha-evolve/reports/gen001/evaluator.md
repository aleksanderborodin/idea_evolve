# Evaluator Report — Generation 1

**strategic_shift: false**

## 1. What did I try?

I processed 14 solutions from 2 productive agents (explore_1: 10, full_1: 4), plus reports from explore_2 (timed out, 0 solutions) and research_1 (findings only). All solutions had valid `.score` sidecar files — no re-evaluation was needed.

For each solution, I:
- Read the score file and solution code
- Identified which ideas (existing and novel) were used
- Tracked the incremental optimization trajectory within each agent
- Cross-referenced agent reports for context on design decisions and failures
- Created/updated 13 idea files (9 updated, 4 new)
- Identified 4 patterns
- Defined 2 clusters
- Built the solution-idea map and coverage matrix
- Wrote the initial State of Affairs (gen1 bootstrap)

## 2. What information did I lack?

- **Detailed per-size timing breakdown within solutions**: The `.score` files give total times per size, but not the breakdown of time spent in packing vs micro-kernel vs stores. This would help prioritize optimizations.
- **Assembly output**: No solution provided disassembly. Understanding actual register allocation and instruction scheduling in the compiler output would reveal whether theoretical improvements translate to real gains.
- **`perf stat` hardware counter data**: Cache miss rates, TLB miss rates, branch mispredictions, port utilization — these would explain phenomena like the NC=512 regression.
- **Whether the benchmark harness aligns C to 64 bytes**: This affects whether streaming stores (`_mm512_stream_si512`) can be used safely. Solutions check at runtime but the default alignment is unknown.

## 3. What given facts might be wrong or outdated?

- **fact_004 instruction latencies**: The `vpmovzxbd` 3c latency claim may be inaccurate for Tiger Lake specifically. full_1 noted this could affect the int32-in-loop approach's penalty.
- **Research Finding 7 truth table values (0xCA/0xAC)** vs **explore_1's values (0xD8/0xE4)**: Both produce correct results (verified by evaluation), but the discrepancy in imm8 values means operand orders differ. This is not wrong per se, but could cause confusion if agents mix conventions.
- **Baseline score of ~770 µs**: Both agents' first solutions (explore_1/sol01: 654 µs, full_1/sol01: 602 µs) already beat this, suggesting the baseline may be worse than 770 µs or that even a basic AVX-512 port provides immediate improvement.

## 4. Was the State of Affairs accurate?

No prior State of Affairs existed (gen 1). I created the initial one. The pre-concatenated knowledge dump accurately reflected all 9 initial ideas and was useful for understanding the starting knowledge base.

## 5. What would I do differently with more or different context?

- If I had `perf stat` data, I could have made more precise predictions about which unexplored combinations would be most productive.
- With assembly dumps, I could have identified specific compiler-generated bottlenecks and suggested targeted intrinsic or scheduling changes.
- A helper that summarizes the optimization trajectory of each agent (before/after scores per change) would have saved many turns of cross-referencing solution code and reports.

## 6. Specific experiments to run

1. **Assembly analysis of explore_1/sol10**: Compile with `-S -O3 -march=native`, inspect the micro-kernel hot loop. Look for: register spills, unnecessary moves, suboptimal instruction scheduling, missed vectorization opportunities.

2. **NC sweep**: Test NC = 64, 128, 192, 256, 384, 512, 1024 on the best solution. Measure per-size impact. This will resolve pattern_002 (NC=256 > NC=512) and potentially find a better NC.

3. **No-packing kernel (idea_013)**: Write a version of sol10 that reads B directly without packing. Benchmark specifically on small (where B=2KB fits in L1) and compare.

4. **8-row kernel with int8 accumulation**: Retry idea_009 using `_mm512_add_epi8` in the k-loop (1 zmm per row instead of 2). This halves register pressure vs the int16 approach that failed in sol03.

5. **perf stat comparison**: Run the best solution with `perf stat -e cache-misses,dTLB-load-misses,instructions,cycles` at NC=256 and NC=512 to diagnose the regression.

6. **Software prefetching**: Add `_mm_prefetch(&B_packed[next_chunk], _MM_HINT_T0)` before each micro-kernel call to hide B-panel load latency for the large benchmark.

7. **Per-phase timing**: Instrument sol10 to separately measure pack_A, pack_B, micro-kernel, and store times. This tells us where the remaining time goes.

## 7. What surprised me?

- **Magnitude of gen1 improvement**: 5.20x speedup in a single generation far exceeds the 1.6x target. The target of 477 µs was beaten by 7 of 14 solutions.
- **Memset as dominant cost**: Neither the problem description nor initial ideas mentioned memset elimination. It was discovered empirically and turned out to be the single biggest optimization (pattern_001).
- **pack_B > micro-kernel as bottleneck**: The initial ideas focused on micro-kernel compute, but vectorizing pack_B was the second-biggest win. The packing infrastructure was under-optimized relative to the compute kernel.
- **NC=512 regression mystery**: Theoretically sound (fewer pack calls, B still fits in L1) but consistently slower. This is a genuine puzzle that needs hardware profiling.
- **explore_1's remarkable productivity**: 10 solutions with a clear improvement trajectory (sol01: 654 → sol10: 148 µs, 4.4x improvement through incremental refinement). The evaluate-immediately workflow worked exactly as intended.
- **Independent convergence**: explore_1 and full_1 independently discovered the memset-skip optimization — it's a natural consequence of understanding the data flow.

## 8. Helper tools feedback

I did not use any helpers from `problem/helpers/`. The evaluation was done entirely by reading `.score` files. No bugs or issues found.

A useful helper would be: **a score summary utility** that reads all `.score` files in a generation directory and outputs a sorted table. Currently I had to read each file individually and compile the table manually — this took significant turns.

## 9. Time budget

Had enough time to complete all required outputs. If I had more time I would:
1. Read every solution's code in detail (I only read the top 3 and the reports for others)
2. Cross-validate the vpternlogd truth table discrepancy between explore_1 and research_1
3. Analyze the specific per-size performance characteristics more deeply (which sizes have the most remaining headroom?)
4. Create more granular ideas separating "int8 accumulation" from "int16 accumulation" as distinct sub-ideas of idea_004

## Output Files Written

| File | Path | Description |
|---|---|---|
| Updated ideas (9) | output/updated_ideas/idea_001-009.md | All existing ideas updated with gen1 evidence |
| New ideas (4) | output/new_ideas/idea_010-013.md | Memset skip, vpternlogd, stack buffers, no-packing kernel |
| Patterns (4) | output/new_patterns/pattern_001-004.md | Memset dominance, NC=256>512, template I-cache, incremental trajectory |
| Clusters (2) | output/updated_clusters/cluster_001-002.md | AVX-512 Compute, Memory & Tiling |
| Solution-idea map | output/solution_idea_map.md | All 14 solutions mapped to ideas |
| Coverage matrix | output/coverage_matrix.md | Explored + unexplored idea combinations |
| Generation snapshot | output/generation_snapshot.md | Gen1 summary |
| State of Affairs | output/state_of_affairs.md | Initial Layer 0 (gen1 bootstrap) |
| Agent gaps | output/agent_gaps.md | 7 gaps identified |
| This report | output/evaluator_report.md | Debrief |
