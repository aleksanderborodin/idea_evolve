---
type: idea
id: idea_008
name: "Adam to L-BFGS-B hybrid"
lifecycle: active
confidence: 0.5
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_full_1_sol03, gen001_explore_2_sol08, gen001_explore_2_sol12]
contradicted_by: [gen001_explore_1_sol01, gen001_explore_1_sol02]
related_ideas: [idea_001]
cluster: cluster_001
tags: [optimizer, hybrid, l-bfgs, second-order]
---

Use Adam to reach a good basin, then switch to L-BFGS-B (with box constraints f >= 0) for
precision refinement. L-BFGS-B uses curvature information and can refine solutions beyond
what Adam's adaptive gradients achieve.

Gen 1 evidence is mixed:
- L-BFGS from cold start is BAD: explore_1/sol01 (C=1.6904), sol02 (C=1.8111).
- Adam -> L-BFGS-B hybrid: full_1/sol03 (C=1.5178), explore_2/sol08 (C=1.5179),
  explore_2/sol12 (C=1.5179). These are competitive with pure Adam multi-scale.
- explore_1/sol10 (multi-scale Adam -> L-BFGS polish) scored C=1.5178, identical to
  multi-scale Adam alone.

The hybrid approach matches but does not clearly beat pure Adam with multi-scale.
L-BFGS-B may provide more value when combined with basin hopping (perturb then L-BFGS-B
refinement could be faster per round than Adam refinement). This combination is untested.
