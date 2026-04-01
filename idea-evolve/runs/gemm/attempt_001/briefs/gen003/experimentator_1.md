## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py` → fitness = 147.26 µs (row-streaming architecture)
Target: 24 µs (geometric mean of 3 per-size median times, lower is better)
Best per-size: small=3.69 µs, medium=225.55 µs, large=3841.72 µs

**Scoring Metric:** Fitness = `(small × medium × large)^(1/3)` — geometric mean.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/description.md` — Problem definition
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/constraints.md` — Constraints
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/fact_006.md` — C alignment constraint
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/fact_007.md` — Measured DRAM bandwidth
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/experiments/gen002/experimentator_1/observations.md` — Previous experiments
- `/home/sasha/Desktop/project_alpha/idea-evolve/population/gen002/explore_1/sol01.py` — Row-streaming best (your base for experiments)

## Directive

Run three targeted experiments to answer specific open questions. Each experiment should produce clear, quantitative results.

### Experiment 1: Aligned-Buffer + Memcpy Overhead Measurement

**Question:** What is the actual net benefit of aligned-buffer NT stores after accounting for aligned_alloc + memcpy overhead?

**Methodology:**
1. Take `/home/sasha/Desktop/project_alpha/idea-evolve/population/gen002/explore_1/sol01.py` (row-streaming, 147.26 µs)
2. Modify the C++ kernel to add a size-adaptive path:
   ```cpp
   if ((size_t)n * m * sizeof(int) > 8*1024*1024) {
       int* cbuf = (int*)std::aligned_alloc(64, (size_t)n * m * sizeof(int));
       // ... compute into cbuf with _mm512_stream_si512 ...
       _mm_sfence();
       std::memcpy(C, cbuf, (size_t)n * m * sizeof(int));
       std::free(cbuf);
   } else {
       // ... original code with _mm512_storeu_si512 ...
   }
   ```
3. Benchmark all 3 sizes. Compare to base solution.

**What you'll learn:** The experimentator_1 measured NT stores give 2.3x on large in isolation, but the full aligned_alloc + memcpy workaround hasn't been measured end-to-end.

### Experiment 2: Verify fact_004 Port Assignments

**Question:** Are the instruction port assignments in fact_004 correct for Tiger Lake?

**Methodology:**
1. Look up these instructions on uops.info for Tiger Lake (ICL/WilliamCove):
   - `vpopcntb zmm`: fact_004 says port 5; experimentator_1 assembly says port 0/1
   - `vpbroadcastb zmm, r8`: fact_004 says port 5 only
   - `vpternlogq zmm`: both say port 0/5
   - `vpmovsxbw zmm`: experimentator_1 says port 5 only
2. If you can't access uops.info, compile a tight loop of each instruction and measure throughput:
   ```cpp
   // Throughput test: 1000 iterations of same instruction
   // If throughput = 1/cycle → single port; if 0.5/cycle → dual port
   ```
3. Cross-reference with Intel Intrinsics Guide if available on the machine

**What you'll learn:** Correct port assignments determine which instructions are the bottleneck. If vpopcntb is port 0/1 (not port 5), the bottleneck is vpbroadcastb (port 5 only), not popcnt.

### Experiment 3: Small Benchmark Pack-Free Measurement

**Question:** How much time does pack_A consume in the small benchmark, and what happens if we eliminate it?

**Methodology:**
1. The small benchmark: n=32, m=1024, k_bytes=2. A = 128 bytes, B = 2048 bytes.
2. Modify the row-streaming kernel to skip any buffering for small sizes and broadcast A bytes directly from the source array.
3. Try processing all 32 rows with maximally unrolled code (32 accumulators, k_bytes=2 → only 2 iterations of k-loop).
4. Benchmark the small size specifically.

**What you'll learn:** Whether the small benchmark can be pushed below 2 µs. Current: 3.69 µs. If small drops to 1 µs, geomean of (1, 225, 2000) = 77 µs vs (3.69, 225, 2000) = 119 µs — significant.

### Output Format
Write results to:
- `output/observations.md` — Detailed experimental results with tables and analysis
- `output/report.md` — Debrief report
- Any byproduct solutions to `output/solNN.py` with `# fitness:` headers
