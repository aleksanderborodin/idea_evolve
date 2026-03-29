---
type: idea
id: idea_014
name: "Warm-start from published solutions"
lifecycle: established
confidence: 0.95
first_seen: generation_3
last_updated: generation_11
last_confirmed_gen: 11
supported_by: [gen003_research_1_sol01, gen004_research_1_sol01, gen005_exploit_2_sol01, gen005_research_1_sol01, gen005_research_1_sol02, gen005_research_1_sol03, gen005_research_1_sol04, gen005_research_1_sol05, gen006_exploit_1_sol01, gen007_explore_1_sol01, gen008_explore_1_sol01, gen009_exploit_1_sol01, gen009_explore_1_sol01, gen010_exploit_1_sol01, gen010_exploit_2_sol01, gen010_explore_1_sol01, gen010_explore_2_sol01, gen011_explore_1_sol01, gen011_exploit_2_sol01]
contradicted_by: []
related_ideas: [idea_016, idea_018, idea_019, idea_021, idea_022, idea_024]
cluster: cluster_003
tags: [warm-start, published-solutions, AlphaEvolve, TTT-Discover]
---

Use published solution arrays (AlphaEvolve, TTT-Discover) as starting points for
further optimization rather than optimizing from random initialization.

**Status: ESTABLISHED at highest confidence (0.95).** Every frontier score since gen 3
derives from a published solution. The TTT-Discover 30k array (C ~ 1.50286) remains the
foundation of all competitive work through gen 11.

**Gen 11 confirmation:** Both scored solutions use TTT-Discover 30k derivatives:
- explore_1: C = 1.5028628677925082 (NEW OVERALL BEST, delta = -3.24e-9 from gen10 best)
- exploit_2: C = 1.502862868176393

**Critical finding (gen 11):** Loading gen010 entrypoints produces different arrays each
time (~6e-11 variance due to deadline-based CD). Future generations must bake arrays as
numpy literals for reproducibility (pattern_028).

Nine consecutive generations of confirmation. 19 supporting solutions. Confidence maintained at 0.95.
