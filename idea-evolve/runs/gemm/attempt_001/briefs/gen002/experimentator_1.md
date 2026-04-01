## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py` → 148.18 µs (geomean)
Per-size breakdown: small=4.49 µs, medium=228.26 µs, large=3176.31 µs
**TARGET: 24 µs**

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/facts/fact_004.md`

## Directive

You are running controlled experiments to answer specific open questions. Do NOT optimize solutions — produce data and analysis.

### Experiment 1: Per-phase timing instrumentation (HIGHEST PRIORITY)

**Question:** Where does the time go in the best current solution? What fraction is pack_A, pack_B, micro-kernel, and stores?

**Methodology:**
1. Read `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py` and extract the C++ code.
2. Add `rdtsc`-based timing instrumentation around each phase:
   - Before/after `pack_A` calls (total across all blocks)
   - Before/after `pack_B` calls (total across all blocks)
   - Before/after micro-kernel execution (total across all blocks)
   - Total time (should equal sum of parts plus loop overhead)
3. Print the timing breakdown as a table for all 3 benchmark sizes.
4. Run this instrumented version through the evaluation pipeline (or compile and run manually if needed).

**Expected output:** A table like:
```
Size     | pack_A | pack_B | kernel | store | other | total
small    | X µs   | X µs   | X µs   | X µs  | X µs  | X µs
medium   | X µs   | X µs   | X µs   | X µs  | X µs  | X µs
large    | X µs   | X µs   | X µs   | X µs  | X µs  | X µs
```

### Experiment 2: Assembly quality inspection

**Question:** Is the compiler generating optimal code for the micro-kernel?

**Methodology:**
1. Compile the best solution's C++ with `-S -O3 -march=native -fverbose-asm`.
2. Find the micro-kernel inner loop in the assembly output.
3. Count: register spills, unnecessary loads/stores, loop overhead instructions.
4. Check: is the k-loop fully unrolled? Are vpternlogd and vpopcntb interleaved with loads?
5. Identify the critical path length in cycles.

### Experiment 3: NC sweep

**Question:** What is the optimal NC for each benchmark size?

**Methodology:**
1. Take the best solution and parameterize NC as a variable.
2. Test NC ∈ {64, 128, 192, 256, 384} on all 3 sizes.
3. Report per-size times for each NC value.

### Experiment 4: Memory bandwidth measurement

**Question:** What is the actual DRAM write bandwidth on this machine? Is the large benchmark hitting the bandwidth ceiling?

**Methodology:**
1. Write a simple C++ benchmark that does `_mm512_stream_si512` writes to a 32MB buffer (matching large benchmark C size). Measure bandwidth.
2. Compare with `memset` bandwidth on the same buffer.
3. Compare with the actual large benchmark time minus pack+kernel time (from Experiment 1).

**Output format:**
Write all results to `output/report.md` with clear tables and analysis. For each experiment, state: question, methodology, raw results, interpretation, and implications for the 24 µs target.

**IMPORTANT:** Start with Experiment 1 immediately — it has the highest information value. The timing breakdown will tell us exactly where optimization effort should focus.
