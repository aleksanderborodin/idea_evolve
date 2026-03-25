---
type: pattern
id: pattern_002
name: "Symmetric initializations converge to worse minima"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol01, gen001_explore_2_sol01, gen001_explore_2_sol07]
related_ideas: [idea_003, idea_012]
tags: [symmetry, initialization, convergence]
---

Solutions initialized with symmetric functions (centered Gaussian, Hann window,
centered raised cosine) consistently score worse than flat+noise or asymmetric
initializations.

- Hann window: C = 3.0 (catastrophic)
- Centered Gaussian (N=800): C = 1.5207 (worse than baseline 1.5185)
- Gaussian mixture K=8: C = 1.5801

This is explained by the mathematical fact that C >= 2 for symmetric functions.
Symmetric initializations must first break symmetry through gradient noise before
making progress, wasting optimization budget.
