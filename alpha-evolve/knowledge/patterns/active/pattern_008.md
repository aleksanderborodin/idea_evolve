---
type: pattern
id: pattern_008
name: "Float32/float64 precision mismatch corrupts optimization decisions"
lifecycle: active
confidence: 0.95
first_seen: generation_5
last_updated: generation_5
evidence: [gen005_exploit_1_sol01, gen005_exploit_2_sol01]
related_ideas: [idea_019, idea_017, idea_009]
tags: [precision, float32, float64, JAX, numerical, bug]
---

The helpers (`compute_c` in helpers/core.py, `sensitivity_map` in helpers/sensitivity.py)
use JAX float32, while `validate.py` (the ground truth evaluator) uses numpy float64.
This precision mismatch has critical consequences for micro-optimization:

1. **Gradient rankings are completely different.** exploit_2 found that the top-20 most
   sensitive elements differ entirely between float32 and float64. Element 48 is #1 in
   float32; element 3236 is #1 in float64. Any optimization guided by float32 sensitivity
   analysis is misguided for well-optimized solutions.

2. **Accept/reject decisions are corrupted.** exploit_2's first attempt (float32 coordinate
   descent) found 1 "improvement" that turned out to be false when validated in float64.
   The C values differ by ~1e-6 between float32 and float64, making improvements smaller
   than 1e-6 undetectable.

3. **Previous results may be affected.** Pattern_007 (published solutions are local minima
   for smooth-max Adam) was tested with float32 compute_c. Some accept/reject decisions in
   gen 4 exploit runs may have been corrupted by float32 noise.

**Implication:** All optimization of well-optimized solutions (C < 1.505) MUST use float64
throughout. The existing helpers are adequate for quick sanity checks but dangerous as
optimization oracles. A float64 compute_c matching validate.py is needed.
