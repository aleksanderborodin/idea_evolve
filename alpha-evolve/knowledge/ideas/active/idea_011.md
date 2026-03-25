---
type: idea
id: idea_011
name: "Lion optimizer for escaping plateaus"
lifecycle: active
confidence: 0.35
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_2_sol09]
contradicted_by: []
related_ideas: [idea_001, idea_008]
cluster: cluster_001
tags: [lion, optimizer, sign-gradient]
---

Use the Lion optimizer (sign-based gradient updates) as a warmup phase before
Adam. Lion's sign-gradient property may escape plateaus that Adam gets stuck in.

**Evidence:**
- explore_2/sol08 (Lion 60k + Adam 50k): C = 1.5207
- explore_2/sol09 (Lion 50k + Adam 70k, 4 seeds): C = 1.5182
- explore_2 report claims "Lion > Adam for this objective in the same step budget."

However, explore_2/sol09 at 1.5182 is essentially identical to the baseline (1.5185)
and explore_1/sol04 (pure Adam 80k: 1.5182). The Lion advantage is marginal at best
and may be entirely explained by the multi-seed search in sol09. A controlled
experiment (Lion vs Adam, same total steps, same seeds) is needed.
