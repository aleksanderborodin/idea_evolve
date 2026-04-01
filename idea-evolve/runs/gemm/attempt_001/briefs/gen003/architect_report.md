# Architect Report — Generation 3

## Data Anomalies

1. **Scoring metric was unresolved for 2 generations.** I read `/home/sasha/Desktop/project_alpha/idea-evolve/problem/validate.py` and confirmed it is geometric mean: `math.exp(sum(math.log(t) for t in time_values) / len(time_values))`. This was flagged by 4+ agents in gen 2, in system_recommendations (REC-1, marked CRITICAL), and in experiment_suggestions (EXP-1, marked CRITICAL). Nobody read the 10-line function. All gen-3 briefs now include the resolved answer.

2. **Gen-2 consistency review completely failed.** Agent produced zero output files in 31.9s. The state_of_affairs.md still says `generation: 1`. All gen-3 agents are working from stale strategic context. The gen-3 consistency review (every 3rd gen, triggered this generation) must rewrite it.

3. **Flat score trajectory is misleading.** 148.18 → 147.26 looks like stagnation, but gen 2 actually produced significant knowledge (phase timing, bandwidth measurements, port analysis, new architecture). The score plateau reflects that gen 2 was heavy on measurement/research and light on implementation of the measured improvements. Gen 3 is positioned to cash in on that knowledge.

4. **exploit_1 in gen 2 produced 12 solutions, all regressions.** This is the strongest signal that BLIS is at a local optimum. The exploit wasted its entire budget exploring BLIS parameter space. Gen 3 exploit_1 is explicitly redirected to row-streaming.

5. **bench_harness.cpp was in the Trash.** exploit_1 restored it. Root cause unknown. REC-3 (add to preflight check) is still unresolved. Risk of recurrence.

## Confidence: Medium-High

The plan is well-grounded in gen-2 experimental data. Specific confidence factors:

**High confidence:**
- The scoring metric is definitively resolved
- NT stores give 2.3x on large (measured, not estimated)
- Int8 accumulation gives 11-13% (measured)
- Row-streaming is the right base architecture

**Medium confidence:**
- Aligned-buffer + memcpy workaround will have net positive impact (depends on memcpy overhead)
- 8-row int8 kernel can be implemented without register spilling
- vpshufb LUT will produce useful information even if not faster

**Low confidence:**
- Whether the combined full-stack (explore_1) can achieve 40-70 µs
- Whether any gen-3 agent will break below 100 µs
- Whether the 24 µs target is achievable at all

## What Didn't Fit

- **Second Track B explore.** Could have assigned an explore to revisit VNNI with repacked input format (research_1 Q3 asks about this). Deferred to research — if research_1 finds a viable VNNI approach, gen 4 should implement it.

- **Medium-specific optimization agent.** Medium (225 µs) has the least headroom (~80 µs floor). A dedicated agent tuning NC, prefetching, and loop order for medium specifically could help. But the full-stack agents should cover this implicitly.

- **perf stat profiling.** `perf_event_paranoid` blocks perf stat in the sandbox. Hardware counters would definitively resolve port bottleneck questions. Only the experimentator's throughput-loop methodology can approximate this.

## Strategic Risks

1. **If both Track A agents fail correctness:** Gen 3 produces no score improvement and only Track B data. The vpshufb approach is unlikely to beat 147 µs on first attempt. We'd need gen 4 to pick up the NT store + int8 work.

2. **If aligned-buffer memcpy is too slow:** The entire "optimize large via NT stores" strategy fails. We'd need to focus entirely on medium (make the geomean dominated by medium improvement). This would be a strategic pivot.

3. **If the experimentator's fact_004 verification shows different port assignments:** The bottleneck analysis changes, potentially invalidating the vpshufb rationale.

## Open Questions for the System Critic

1. **Should we recommend the user lower perf_event_paranoid?** Hardware counter data would be worth more than an entire experimentator session. One `perf stat` run would resolve the port bottleneck dispute definitively.

2. **Is the 24 µs target a "stretch goal" or a hard requirement?** If it's a stretch goal, agents should be told the realistic target is 60-80 µs. If it's a hard requirement, we need to investigate whether the problem setup allows non-standard output (e.g., not writing full int32 C).

3. **What happened to bench_harness.cpp?** Until we know the root cause of its deletion, any gen-3 agent could accidentally repeat it. The preflight check (REC-11) should be implemented before gen 4.
