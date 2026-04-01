# Evaluator Report — Generation 3

**strategic_shift: false**

## Executive Summary

Gen003 achieved a **marginal 4.3% score improvement** (141.0 µs, from 147.26 µs) but produced
**significant negative knowledge** that eliminates several previously promising directions.
The generation's primary contribution is establishing that the row-streaming kernel is
**memory-bandwidth-bound** (pattern_011) and that future improvement must come from memory
traffic reduction, not compute optimization.

Three new high-leverage ideas emerged (idea_020 multi-threading, idea_021 SSE NT stores,
idea_022 4-row B-amortization), all untested. Gen004 should focus exclusively on these.

## 1. What Did I Try?

### Score Collection
- Read `.score` files for all 22 solutions across 4 code-producing agents
- Exploit_1 had only 1 of 13 solutions scored in population directory (sol02 at 141.0 µs)
- Explore_1: 4 solutions, all valid (168-220 µs)
- Explore_2: 5 solutions, all valid (342-534 µs)
- Experimentator_1: 3 solutions reported but in experiment directory, not population
- Research_1: 0 solutions (pure research)

### Knowledge Analysis
- Analyzed all 6 agent debrief reports for cross-cutting findings
- Updated 8 existing ideas, created 3 new ideas + 1 new fact
- Created 3 new patterns documenting gen003's key discoveries
- Updated all 3 clusters
- Debunked idea_018 (vpshufb LUT), archived idea_013 (no-pack direct)
- Promoted idea_014 (row-streaming) to established
- Built complete solution-idea map for gen003 (13 entries)
- Updated coverage matrix with gen003 data and new unexplored combinations

## 2. What Information Did I Lack?

- **Experimentator_1's detailed scores** were only available in the report, not as `.score`
  files in the population directory. This made it harder to incorporate them into rankings.
- **Exploit_1's 12 unscored solutions** — the agent report describes scores for many of these
  but the `.score` files don't exist in the population directory. Some of these (sol03 at
  152 µs, sol11 at 181 µs) would be useful data points.
- **Whether the experimentator's port microbenchmark methodology is reliable.** The throughput
  loop approach can be affected by frequency scaling, dead-code elimination, and microcode
  effects. The port assignments (fact_008) should be considered 0.9 confidence, not 1.0.

## 3. What Given Facts Might Be Wrong or Outdated?

- **fact_004 (instruction port assignments):** The claim that vpopcntb is port 5 is now
  contradicted by experimentator_1's microbenchmark (fact_008: vpopcntb is port 0/1). fact_004
  should be updated or deprecated.
- **idea_015 confidence 0.7:** Was based on gen002's standalone 2.3x measurement. Gen003
  showed this doesn't translate to integrated kernels. Lowered to 0.4.
- **The 24 µs target:** Multiple agents (research_1, experimentator_1, exploit_1) independently
  concluded this is physically impossible given measured DRAM bandwidth. Medium alone has a
  ~220 µs bandwidth floor. Even with perfect large optimization, geomean cannot go below
  ~90 µs. The realistic target is 60-80 µs.

## 4. Was the State of Affairs Accurate?

**The State of Affairs is critically stale** — it still says "Generation 1" because the gen002
consistency review failed (zero output in 31.9s). Key inaccuracies:

- Lists 148.18 µs as best (now 141.0 µs)
- Doesn't mention the row-streaming architecture (idea_014) or its promotion to established
- Doesn't reflect the memory bandwidth wall finding (pattern_011)
- Lists several "unexplored" items that have been explored and debunked in gen002-003
- Doesn't mention the C alignment constraint (fact_006) or its implications

The gen003 consistency review MUST rewrite the SoA. This is the highest-priority meta-task.

## 5. What Would I Do Differently With More or Different Context?

- Run `evaluate.py` on exploit_1's unscored solutions to capture their scores. The report
  describes sol03 (152 µs) and sol11 (181 µs) which would improve the rankings data.
- Cross-reference experimentator_1's port microbenchmark with Agner Fog's instruction tables
  for Tiger Lake to validate fact_008 independently.
- Check whether the dashboard correctly displays gen003 scores and rankings.

## 6. Specific Experiments to Run

### Highest Priority (gen004 must implement)
1. **4-row ternlogd+popcnt kernel** (idea_022): Take gen003/exploit_1/sol02 (141 µs),
   add 4-row B-load sharing. Expected: ~80-95 µs based on explore_2's 1.55-1.67x data.

2. **SSE 128-bit NT stores, size-adaptive** (idea_021): Take the best kernel, replace
   `_mm512_storeu_si512` with 4× `_mm_stream_si128` only when `n*m*4 > 8MB`. Add
   `_mm_sfence()`. Expected: large 3841→~1350 µs, geomean ~105 µs.

3. **Combined: 4-row + SSE NT stores**: Combine experiments 1+2. Expected: ~60-80 µs.

### High Priority
4. **Measure C alignment per benchmark size**: Add fprintf to gemmCandidate. Conclusively
   answer whether 512-bit NT stores work for large benchmark C.

5. **Assembly inspection of best solution**: Compile with `-S -fverbose-asm`, inspect inner
   loop for register spills, instruction scheduling, and port pressure.

6. **Cgroup thread verification**: Test whether pthread_create works within the cgexec cgroup.
   If yes, implement 2-thread gemmCandidate (idea_020).

### Lower Priority
7. **Column-blocked output with 4-row kernel**: Process NC=256 columns for all 4 rows before
   advancing. Tests whether C tile stays in L1 (4×256×4 = 4 KB ≪ 48 KB L1).

8. **Benchmark variance study**: Run the same solution 50 times to measure the actual variance
   distribution. Determine the minimum reliable improvement threshold.

## 7. What Surprised Me?

1. **Only 1 of exploit_1's 13 solutions had a score file.** The agent evaluated many solutions
   (per its report) but only sol02's score was preserved. This suggests a systematic issue
   with `.score` file creation or routing in the orchestrator.

2. **The convergence of independent analyses.** Three different agents (exploit_1, explore_1,
   experimentator_1) independently concluded the kernel is memory-bandwidth-bound. The fact
   that they reached the same conclusion via different approaches (failed optimizations, timing
   analysis, bandwidth calculations) gives high confidence in pattern_011.

3. **vpshufb's poor performance.** The hypothesis that changing instruction ports would help
   was reasonable, but the port assignment was wrong (vpshufb IS port 5) and the overhead of
   nibble extraction made it worse regardless.

4. **Sol02's improvement is likely fragile.** A 4.3% improvement that may come from a dead
   code branch changing instruction alignment is not a robust optimization. The next compiler
   update could eliminate or reverse it.

## 8. Helper Tools Feedback

Did not use any helpers from `problem/helpers/`. The evaluator role is analysis, not code
generation.

**Helper that would help future evaluators:** A script that re-runs evaluation on all
solutions in a generation that are missing `.score` files. This would catch the exploit_1
scoring gap automatically.

## 9. Time Budget

Had sufficient time to complete all required analysis. The comprehensive reading of all
6 agent reports, 22 solutions, and the full knowledge base was thorough.

If I had more time, I would:
1. Run `evaluate.py` on exploit_1's unscored solutions
2. Investigate why exploit_1's scores weren't preserved
3. Create a more detailed bandwidth analysis quantifying the exact theoretical floor per
   benchmark size
