---
type: pattern
id: pattern_018
name: "Perturbation hierarchy breaks down at k=5 (quintuplets hit float64 noise floor)"
lifecycle: active
confidence: 0.75
first_seen: generation_9
last_updated: generation_9
evidence: [gen009_explore_1_sol01]
related_ideas: [idea_022, idea_021, idea_019]
tags: [quintuplet, perturbation, precision-limit, float64, noise-floor]
---

The perturbation hierarchy (coord descent → triplets → quadruplets → quintuplets)
does NOT extend indefinitely. Quintuplets (k=5, d1+...+d5=0) find only noise-floor
improvements at the current solution precision.

**Gen 9 evidence (explore_1):**
- 50k quintuplet trials with 3 strategies (S0, S1, S3) and 9 step sizes
- **2 improvements found, delta_C = -4.4e-16 = 1 ULP of float64**
- These are floating-point rounding artifacts, not genuine optimization

**Why quintuplets fail while quadruplets succeeded:**
- Quintuplet gradient g values are ~3e-5 in magnitude
- Projected gradient g_proj ~ 2.4e-5
- At the smallest viable step size (alpha=1e-6), deltas are ~2.4e-11
- The incremental autoconv update has numerical noise at this scale
- The 4 free variables provide no additional expressivity beyond noise

**Gen 9 also showed quintuplets do NOT unlock quadruplets:**
- After 2 quintuplet improvements, 20k quadruplet follow-up found 0 improvements
- The unlocking effect (pattern_014) does NOT continue from k=4 to k=5

**Implication:** The useful perturbation hierarchy for this problem is:
coord descent (k=1) → triplets (k=3) → quadruplets (k=4) → STOP.
Pair-wise (k=2) and quintuplets (k=5) are both ineffective (for different reasons:
pairs due to stationarity, quintuplets due to float64 precision limits).

**Rate comparison:** Triplets 424 t/s, quadruplets 165 t/s, quintuplets 165 t/s.
Triplets are most efficient per wall-clock second.
