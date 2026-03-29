---
type: pattern
id: pattern_010
name: "Full-array scan outperforms gradient-guided element selection"
lifecycle: active
confidence: 0.8
first_seen: generation_6
last_updated: generation_6
evidence: [gen006_exploit_1_sol01]
related_ideas: [idea_019, idea_017]
tags: [coordinate-descent, gradient, element-selection, full-scan]
---

When performing coordinate descent on well-optimized solutions (C < 1.503), scanning
ALL nonzero elements vastly outperforms selecting elements by gradient magnitude.

**Evidence (gen 6 exploit_1):**
- Gradient-guided top-2000 elements: 5340 improvements
- Full-array scan of all 25141 nonzero elements: 8883 additional improvements (~60% more)
- The JAX smooth-max gradient (logsumexp) is an imperfect proxy for which elements are
  actually improvable. It correctly identifies SOME good candidates but misses the majority.

**Root cause:** The smooth-max gradient at low temperature is nearly uniform in the
denominator term (~-0.539 everywhere), and the numerator term depends on a single argmax
element. This creates an unreliable ranking where small numerical differences determine
which elements appear "most important" — but these differences don't correlate well with
actual improvability via perturbation.

**Implication:** Future coordinate descent agents should skip gradient computation entirely
and go straight to full-array scan. The O(N) incremental autoconvolution update makes this
feasible even at N=30000 (28x faster than FFT per element).
