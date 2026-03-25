---
type: idea
id: idea_003
name: "Function shape priors"
lifecycle: active
confidence: 0.4
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: []
contradicted_by: [gen001_explore_1_sol03]
related_ideas: [idea_006, idea_011]
cluster: cluster_002
tags: [initialization, function-shape]
---

Initialize with known function families with good autoconvolution properties. Gen 1 tested
cosine window initialization (explore_1/sol03, C=1.5257) which did NOT improve over standard
flat block init + optimization (explore_1/sol04, C=1.5178). The flat block centered on the
middle half of the domain remains a reliable starting point.

However, research_1 identified that two-bump and Sidon-set-inspired initializations are
theoretically motivated (see idea_011). These have NOT been tested yet and may offer
fundamentally different basins of attraction. The failure of cosine window init does not
invalidate multi-bump priors — it only shows that smooth unimodal priors don't help.
