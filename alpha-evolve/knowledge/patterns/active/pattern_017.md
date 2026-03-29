---
type: pattern
id: pattern_017
name: "Ultra-fine coordinate descent deltas reopen thousands of improvements"
lifecycle: active
confidence: 0.7
first_seen: generation_9
last_updated: generation_9
evidence: [gen009_exploit_1_sol01]
related_ideas: [idea_019]
tags: [coordinate-descent, delta-resolution, ultra-fine, convergence, non-monotonic]
---

When coordinate descent is declared "converged" at delta scales 1e-2 to 1e-7,
extending the delta grid to 1e-8 through 1e-11 reopens thousands of improvements.

**Gen 9 evidence (exploit_1):**
- Standard deltas (1e-2 to 1e-7): 1209 improvements, delta_C = -2.71e-11
- Ultra-fine deltas (1e-8 to 1e-10): **4943 improvements**, delta_C = -2.26e-10
- Finest deltas (5e-8 to 5e-11): 375 improvements, delta_C = -2.34e-12

The ultra-fine pass found **4x more improvements** than the standard pass.

**Non-monotonic improvement counts within ultra-fine pass:**
Rounds: 529 → 1323 → 1877 → 1214. Round 3 found MORE improvements than rounds 1-2.
This suggests cascading effects: fine changes at one element create new fine-scale
opportunities at distant elements through the autoconvolution coupling.

**Implication:** Previous pattern_012 ("coordinate descent convergence is exponentially
decaying") is true only for a fixed delta grid. The landscape has rich fine-scale
structure that is invisible to coarse deltas. Using geometric delta spacing
(np.geomspace(1e-12, 1e-2, 50)) would ensure comprehensive coverage.

**Performance note:** Ultra-fine CD runs efficiently because each individual element
trial is O(N) via incremental autoconv update, and fine deltas don't change the
asymptotic cost. Total eval time for the baked result is 0.085s.
