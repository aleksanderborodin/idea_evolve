---
type: pattern
id: pattern_004
name: "N=600 outperforms higher N at current optimization quality"
lifecycle: active
confidence: 0.65
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_full_1_sol03, gen001_full_1_sol04, gen001_explore_1_sol01]
related_ideas: [idea_002]
tags: [resolution, N, performance]
---

At the current optimization level, N=600 produces better scores than N=800
or N=1000, because fewer parameters means faster iterations and more
exploration in fixed wall-clock time.

- N=600, smooth-max, 8 seeds: C = 1.5108 (best)
- N=800, smooth-max, 12 seeds: C = 1.5151
- N=800, standard, 3 seeds: C = 1.5207
- N=1000, standard, 4 seeds: C = 1.5182

This pattern may reverse when optimization quality improves sufficiently
that fine-scale structure matters (approaching C ~ 1.503).
