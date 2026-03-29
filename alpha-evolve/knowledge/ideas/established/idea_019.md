---
type: idea
id: idea_019
name: "Float64 coordinate descent on published solutions"
lifecycle: established
confidence: 0.95
first_seen: generation_5
last_updated: generation_11
last_confirmed_gen: 11
supported_by: [gen005_exploit_2_sol01, gen006_exploit_1_sol01, gen007_exploit_1_sol01, gen007_exploit_2_sol01, gen007_full_1_sol04, gen008_exploit_1_sol01, gen009_exploit_1_sol01, gen010_exploit_1_sol01, gen010_exploit_2_sol01, gen010_explore_1_sol01, gen010_explore_2_sol01, gen011_explore_1_sol01, gen011_exploit_2_sol01]
contradicted_by: []
related_ideas: [idea_017, idea_014, idea_009, idea_021, idea_022, idea_024]
cluster: cluster_001
tags: [coordinate-descent, float64, micro-optimization, published-solutions, ultra-fine-deltas, top-K-screening, incremental-drift, focused-deltas]
---

Element-wise coordinate descent on published solution arrays using full float64 precision.
ONLY technique achieving agent-driven improvements over published solutions, confirmed
across seven generations (5-11).

**Gen 11 evidence — 3 agents, NEW OVERALL BEST:**

| Agent | Improvements | Delta C | Method |
|---|---|---|---|
| explore_1 | 10,995 (CD only) + 2,300 (pair pre-phase) | -3.24e-9 | Non-IP pairs + CD (idea_024) |
| exploit_2 | 3,499 (focused) + 1,917 (broad) | -8.4e-13 | Focused vs broad delta comparison |
| exploit_1 | ~50-100/round × 410 rounds | ~1.8e-12 | Per-round FFT resync (from worse start) |

**Gen 11 KEY DISCOVERIES:**

1. **Focused delta grid wins** (pattern_026): np.geomspace(1e-14, 1e-11, 40) finds
   1.83x more improvements/s than broad grid (1e-14 to 1e-1, 100 values). Dead scales
   waste 60% of trial time.

2. **Intra-round drift** (pattern_027): Per-round FFT resync is insufficient at 2000+
   mods/round. Must resync every ~500 modifications to keep drift below improvement scale.

3. **Non-reproducible entrypoints** (pattern_028): Deadline-based solutions produce
   different arrays per invocation (~6e-11 variance). Must bake arrays as literals.

4. **Non-IP pair synergy** (idea_024, pattern_025): Non-integral-preserving 2-element
   moves before CD amplify subsequent CD gains by ~15x. NEW OVERALL BEST achieved via
   this two-phase protocol.

**Recommended gen 12 protocol:**
- Bake best array as numpy literal (instant load)
- Phase 1: Non-IP pair search, 50k-100k trials
- Phase 2: Ultra-fine CD, focused deltas (1e-14 to 1e-11, 40 values)
- FFT resync every 500 modifications
- Top-K screening K=30

**Cumulative evidence:** 13 supporting solutions across 7 generations, 0 contradictions.
Confidence maintained at 0.95.
