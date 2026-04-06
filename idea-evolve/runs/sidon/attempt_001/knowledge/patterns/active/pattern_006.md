---
type: pattern
id: pattern_006
name: "102-element Singer q=101 set is locally saturated (40+ blockers per candidate)"
lifecycle: active
confidence: 0.85
first_seen: generation_2
last_updated: generation_2
evidence: [gen002_exploit_1_sol01, gen002_exploit_2_sol03, gen002_exploit_2_sol04]
related_ideas: [idea_008, idea_012, idea_010]
tags: [saturation, barrier, singer-101, blockers]
---

The 102-element Singer q=101 truncated set has extreme local saturation: every non-member
element in {0, ..., 10000} has at least 40 "blockers" — existing set members whose differences
would collide if the non-member were added.

Evidence:
- exploit_1: exhaustive single-removal (102 trials, net zero), exhaustive pair-removal (5151 pairs, net zero)
- exploit_2/sol03: SA from 102-element base, 114 seconds, no improvement
- exploit_2/sol04: partial shifts + greedy extension, no improvement

The 40-blocker minimum contrasts sharply with Singer q=97 perturbation, where some candidates
had only 4-10 blockers (enabling the 98→99 improvement). The q=101 set uses 5151/10000
differences (51.5%) vs q=97's 4753/9506 (50%), but the structured distribution creates far
stronger blocking.

**Implication**: No local search method (SA, k-opt for small k, greedy perturbation) can
improve on 102 from the Singer q=101 base. Breaking 102 requires either:
1. A fundamentally different construction method
2. Very large perturbation (k≥40 removals), which is likely counterproductive
3. Computational search with ILP/constraint programming
