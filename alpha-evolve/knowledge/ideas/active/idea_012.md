---
type: idea
id: idea_012
name: "Multi-start with diverse initializations"
lifecycle: active
confidence: 0.6
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol09]
contradicted_by: []
related_ideas: [idea_007, idea_003]
cluster: cluster_001
tags: [multi-start, initialization-diversity, global-optimization]
---

Run optimization from 3-5+ diverse starting points and keep the best result. Different
initializations (flat block, narrow block, wide block, two-bump) converge to different
local minima; selecting the best bypasses the single-basin limitation.

Gen 1 evidence: explore_1/sol09 used 5 diverse initializations (flat, narrow, wide, two-bump,
random) at N=600, selected best, then refined at N=2000. Scored C=1.5174, better than
single-start multi-scale (sol04, C=1.5178) but worse than basin hopping (sol11-12, C=1.5168).

Multi-start addresses a different problem than basin hopping: it samples different basins
initially, while basin hopping explores around one basin. Combining both (multi-start + basin
hopping from the best) is untested and could improve results further.
