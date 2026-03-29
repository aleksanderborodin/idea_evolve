---
type: pattern
id: pattern_015
name: "Downsampling TTT-Discover 30k destroys solution structure"
lifecycle: active
confidence: 0.9
first_seen: generation_8
last_updated: generation_8
evidence: [gen008_explore_2_observations]
related_ideas: [idea_020, idea_014, idea_018]
tags: [downsampling, interpolation, resolution, LP, structure]
---

Downsampling the TTT-Discover 30k array to intermediate resolutions (N=5000-10000)
via interpolation produces solutions with C=3-7, far from the original C=1.503.
The function's fine structure (many near-zero values between support regions)
interpolates poorly.

**Evidence (gen 8 explore_2):**

| N target | C after interpolation |
|----------|----------------------|
| 5000     | 7.289                |
| 8000     | 3.058                |
| 10000    | 4.094                |
| 30000    | 1.5029 (original)    |

**Implication:** The LP plateau analysis at intermediate N cannot be done by
downsampling. It requires fresh optimization from scratch at each target N
(gradient descent or other method to reach near-optimal, then measure tight
constraint count). This significantly increases the effort needed to answer
whether LP is tractable at intermediate resolution.

**Corollary:** The TTT-Discover solution's structure is inherently high-resolution.
Its quality derives from fine-grained control of 30k elements, not from a shape
that can be represented at lower resolution. This is consistent with the
LP-guided nature of its construction (LP operates on all elements simultaneously).
