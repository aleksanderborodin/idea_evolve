---
type: pattern
id: pattern_019
name: "LP plateau is resolution-independent near optimality"
lifecycle: active
confidence: 0.8
first_seen: generation_9
last_updated: generation_9
evidence: [gen009_explore_2_sol01, gen009_explore_2_sol02]
related_ideas: [idea_020, idea_018]
tags: [LP, plateau, resolution, tight-constraints, resolution-independence]
---

The autoconvolution plateau that defeats LP refinement is not an artifact of high
resolution (N=30k). The same relative plateau fraction appears at any N near optimality.

**Gen 9 evidence (explore_2):**

| N | Near-optimal C | Tight@1e-5 (count) | Tight@1e-5 (fraction) |
|---|---|---|---|
| 5000 | 1.517 | 2396-2827 | 24-28% |
| 30000 | 1.503 | ~6500 | ~30.5% |

The tight constraint fraction at N=5000 near-optimal (24-28%) is comparable to
N=30k near-optimal (~30.5%). This is NOT what was expected: gen 8 explored N=5000
at C=1.679 (far from optimal) and found only 0.03-0.11% tight constraints, leading
to the hypothesis that LP might be tractable at intermediate N near optimality.

**The critical distinction:** Far from optimality (C >> C_opt), the plateau is small.
Near optimality, the plateau grows to ~25-32% of autoconv points regardless of N.
This is a mathematical property of the problem structure, not a resolution artifact.

**Consequence:** LP refinement is fundamentally blocked at ALL resolutions near
optimality. The gen 8 hypothesis ("if tight@1e-5 < 500: LP may work") was wrong
because it extrapolated from far-from-optimal behavior.

**Also confirmed:** N=5000 optimization floor is C≈1.517, far above the N=30k
frontier of C≈1.503. The TTT-Discover N=30k array captures structure that 5000
elements cannot represent.
