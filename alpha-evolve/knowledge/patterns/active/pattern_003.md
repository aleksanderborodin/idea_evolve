---
type: pattern
id: pattern_003
name: "Diminishing returns from more optimizer steps"
lifecycle: active
confidence: 0.7
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol04, gen001_explore_2_sol09]
related_ideas: [idea_001, idea_007]
tags: [convergence, diminishing-returns, steps]
---

Doubling or tripling the number of Adam steps yields only marginal improvements
when using the standard (true max) objective:
- 40k steps: C = 1.5185 (baseline)
- 80k steps: C = 1.5182 (explore_1/sol04)
- 120k steps (Lion+Adam): C = 1.5182 (explore_2/sol09)

The optimizer converges to a local minimum by ~40k steps and additional
steps only provide negligible refinement. This contrasts with the smooth-max
approach (idea_007), which changes the landscape itself to enable continued
progress.

This pattern suggests that algorithmic changes (smooth-max, better initialization
strategy) are more valuable than more compute on the same algorithm.
