---
type: idea
id: idea_011
name: "Lion optimizer for escaping plateaus"
lifecycle: archived
confidence: 0.15
first_seen: generation_1
last_updated: generation_6
last_confirmed_gen: 1
supported_by: [gen001_explore_2_sol09]
contradicted_by: []
related_ideas: [idea_001, idea_008]
cluster: cluster_001
tags: [lion, optimizer, sign-gradient, archived]
---

Use the Lion optimizer (sign-based gradient updates) as a warmup phase before Adam.

**ARCHIVED — marginal evidence, at staleness threshold, pipeline has moved on.**

**Gen 1 evidence:**
- explore_2/sol09 (Lion 50k + Adam 70k, 4 seeds): C = 1.5182
- This is identical to pure Adam 80k (explore_1/sol04: 1.5182).
- The Lion "advantage" is fully explained by multi-seed search, not Lion itself.

Never retested in gens 2-6. A controlled experiment (Lion vs Adam, same seeds) was
never conducted. The pipeline has moved entirely past gradient descent from random
init — the frontier is now coordinate descent and LP on published solutions, where
Lion is irrelevant.

Confidence lowered to 0.15. Archiving due to staleness and irrelevance to frontier.
