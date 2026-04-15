---
type: pattern
id: pattern_001
name: "Greedy Baselines Plateau Well Below Algebraic Bounds"
lifecycle: confirmed
confidence: 1.0
first_seen: gen000
last_updated: gen001
evidence: [gen000_baseline_sol01]
related_ideas: [idea_001, idea_002]
tags: [greedy, baseline, performance-gap]
---

The greedy nearest-neighbor heuristic with random restarts achieves only 262 on M(8,5), while AGL(1,8) achieves 616 — more than 2× better. This confirms that for this problem, greedy is far from optimal and algebraic/group-theoretic approaches are essential.

The gap is not narrow: 262 vs 616 represents 354 codewords (~54% performance gap). This is the strongest evidence that the search space has deep local optima unreachable by local perturbations.
