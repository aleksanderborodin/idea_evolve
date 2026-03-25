---
type: pattern
id: pattern_003
name: "L-BFGS from cold start underperforms Adam"
lifecycle: confirmed
confidence: 0.85
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol01, gen001_explore_1_sol02]
related_ideas: [idea_001, idea_008]
tags: [optimizer, l-bfgs, failure-mode]
---

L-BFGS (or L-BFGS-B) starting from random/simple initialization converges to poor local
minima with C ~ 1.69-1.81. Adam from the same initializations reaches C ~ 1.52.

explore_1/sol01: L-BFGS + softplus + Gaussian init, N=1000 -> C = 1.6904
explore_1/sol02: L-BFGS + softplus + flat block init, N=600 -> C = 1.8111

The likely explanation: L-BFGS converges too quickly to the nearest local minimum using
curvature information, while Adam's adaptive momentum helps it traverse the non-convex
landscape more effectively. L-BFGS may be useful for refinement after Adam reaches a
good basin (idea_008), but not as the primary optimizer.
