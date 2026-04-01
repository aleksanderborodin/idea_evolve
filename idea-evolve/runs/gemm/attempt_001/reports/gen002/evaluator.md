# Evaluator Report — Generation 2

**strategic_shift: false**

## 1. What Did I Try?

Evaluated all 25 gen002 solutions across 4 agents plus 1 experimentator. Ran
evaluate.py on 8 explore_1 solutions that were missing .score files (all passed
correctness). Analyzed all 6 agent debrief reports. Created 6 new ideas
(idea_014-019), 4 new patterns (pattern_005-008), 2 new facts (fact_006-007),
1 new cluster (cluster_003), and updated 6 existing ideas.

Key evaluation results:
- **Gen002 best:** explore_1/sol01 at **147.26 µs** (small=3.69, med=225.55, large=3841.72)
- **Previous best:** gen001/explore_1/sol10 at 148.18 µs
- **Improvement:** 0.6% — marginal, within measurement noise
- **All exploit_1 solutions regressed** (worst: 393.77 µs, best: 241.78 µs)

## 2. What Information Did I Lack?

- **The actual scoring metric implementation.** The Architect raised whether
  "geometric median" means geometric mean or true median. For 3 values, the
  true median is the middle value (always medium benchmark). This would
  fundamentally change strategy. I couldn't verify without reading evaluate.py
  internals.
- **Whether the .score files from explore_1 were genuinely missing** or if
  there was an output-move issue. I had to re-evaluate all 8 solutions.
- **Experimentator_1's measurements used a specific kernel variant**, not the
  population best. The NC sweep and phase timing data may not be directly
  comparable to explore_1/sol01's architecture.

## 3. What Given Facts Might Be Wrong or Outdated?

- **fact_004 (instruction latencies):** Multiple agents flagged this as
  unverified. The vpopcntb port assignment (port 5 vs port 0/1) is disputed.
  Experimentator_1's assembly analysis says vpbroadcastb is port 5 only and
  vpopcntb is port 0/1, which differs from fact_004.
- **The 30 GB/s bandwidth assumption** in the State of Affairs is too
  conservative. Experimentator measured 24.84 GB/s streaming at 32 MB.
  Regular stores are only 11.38 GB/s. The State of Affairs should be updated
  with measured values.
- **The "24 µs target is impossible" claim** from exploit_1 is likely wrong.
  Research agent's analysis shows geomean(0.5, 80, 640) ≈ 29 µs is
  physically achievable. The target is aggressive but not impossible if NT
  stores work for large.

## 4. Was the State of Affairs Accurate?

Mostly accurate for gen001 data. Updates needed:
- Medium is at bandwidth floor (new finding — pattern_005)
- Packing is negligible, kernel+store dominates (new finding — pattern_006)
- BLIS is at diminishing returns (new finding — pattern_007)
- Row-streaming architecture is competitive (new — idea_014, cluster_003)
- Measured DRAM bandwidth replaces estimates (fact_007)
- C alignment constraint blocks NT stores (fact_006)

The State of Affairs correctly identified all the right open questions
(per-phase timing, assembly quality, NC sweep, bandwidth). Experimentator_1
answered most of them.

## 5. What Would I Do Differently?

- Check the scoring metric first (geomean vs true median) — this changes
  everything about strategic priorities.
- Run evaluate.py on missing solutions in parallel rather than sequentially
  (wasted ~4 minutes on sequential evaluation).
- Read the explore_1 solutions more carefully before evaluating — I could have
  predicted sol01 would be the best based on the debrief report.

## 6. Specific Experiments to Run

### Experiment 1: Aligned Buffer NT Store Workaround (CRITICAL)
Allocate `alignas(64) int C_buf[n*m]` on the heap (or use `_mm_malloc`),
compute with NT stores into C_buf, then `memcpy(C, C_buf, n*m*4)`.
Measure: does the NT store benefit (2.3x on large) survive the memcpy cost?
For large (32 MB), memcpy at ~15 GB/s takes ~2133 µs. NT stores save ~5600 µs.
Net win: ~3467 µs. **This should work.**

### Experiment 2: 8-Row int8 Kernel
Implement the kernel described in research findings (Finding 3).
Test standalone, then combine with existing best architecture.

### Experiment 3: Scoring Metric Verification
Read `problem/evaluate.py` and/or `problem/validate.py` to determine if
"geometric median" means `(a*b*c)^(1/3)` (geometric mean) or the actual
median of sorted values. This determines whether large benchmark matters.

### Experiment 4: Row-Streaming + NT Stores for Large
Take gen002/explore_1/sol01, add size-adaptive NT stores (with aligned buffer
workaround). Expected: large drops from 3842 µs to ~1500-2000 µs, geomean
drops from 147 µs to ~80-100 µs.

### Experiment 5: Combine All Top Ideas
Row-streaming + int8 accum + NT stores (aligned buffer) + adaptive NC.
Expected geomean: ~40-60 µs.

## 7. What Surprised Me?

1. **explore_1/sol01 (simplest row-streaming variant) was the overall best.**
   The 1-row-at-a-time approach with no packing at all matched BLIS. Simplicity
   won over optimization.

2. **ALL 12 exploit_1 variants regressed.** The BLIS local optimum is remarkably
   robust. Changing any single parameter makes things worse. This is a strong
   signal that BLIS improvements require simultaneous multi-parameter changes
   (int8 + 8-row + NT stores all at once).

3. **Medium benchmark is at the bandwidth floor.** At 228 µs vs 247 µs
   theoretical minimum, there's only 8% improvement possible on medium. This
   constrains the geomean target significantly.

4. **The C alignment issue.** The single biggest optimization (NT stores) is
   blocked by a harness implementation detail. This was unknown before gen002.

5. **Discrepancy between agent-reported and evaluator-measured scores.**
   explore_1 reported sol06 as best at 150.04 µs, but my evaluation gives
   sol01 at 147.26 µs as best. Benchmark variability across runs is ~5%.

## 8. Helper Tools Feedback

Did not use any helpers from `problem/helpers/`. No helpers are relevant to the
evaluator's analysis work. A useful helper would be: `helpers/score_summary.py`
— a script that scans a population directory and prints a sorted score table,
saving the evaluator from manually reading .score files.

## 9. Time Budget

Adequate for the evaluation work. The main time cost was running evaluate.py
8 times for explore_1's missing .score files (~4 minutes total). If .score
files had been present, I would have had more time to:
1. Read and analyze the actual solution code for all 25 solutions (I only read
   3 in detail)
2. Verify the scoring metric against evaluate.py source code
3. Create more detailed idea descriptions with code snippets

## Staleness Check

All ideas have `last_confirmed_gen: 1` or `last_confirmed_gen: 2`. No idea is
stale (staleness threshold is 5 generations). The knowledge base is young and
well-maintained.

## Experiment Consolidation

Only gen002 experiments exist in `knowledge/experiments/`. No experiments are
older than 3 generations. No consolidation needed yet.
