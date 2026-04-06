---
type: pattern
id: pattern_003
name: "Singer set is saturated — all differences used exactly once"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol01]
related_ideas: [idea_006, idea_007]
tags: [singer, saturation, algebraic]
---

The Singer difference set for q=97 uses ALL 9506 positive differences {1, ..., 9506} exactly
once. This is the defining property of a perfect (v, k, 1)-difference set. As a consequence,
the Singer set is maximally "saturated" — no element from {0, ..., 9506} can be added without
creating a collision.

This saturation explains why greedy extension of Singer fails: any candidate element generates
98 new differences, all of which must be unused. With 100% difference coverage in {1, ..., 9506},
extensions are only possible using elements from {9507, ..., 10000}, and even those have very
low probability of fitting (each must avoid 98 collisions).

The perturbation approach (idea_007) works by removing 1-3 elements to FREE their ~2-6
differences, creating room for additions. But the room is limited: 99 is consistently
achievable, 100 is not.
