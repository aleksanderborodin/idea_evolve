---
type: pattern
id: pattern_026
name: "Focused delta grid (1e-14 to 1e-11) outperforms broad grid by 1.83x"
lifecycle: active
confidence: 0.8
first_seen: generation_11
last_updated: generation_11
evidence: [gen011_exploit_2_sol01]
related_ideas: [idea_019]
tags: [delta-grid, focused, coordinate-descent, efficiency, speedup]
---

A focused delta grid of np.geomspace(1e-14, 1e-11, 40) finds 1.83x more
improvements per second than the standard broad grid np.geomspace(1e-14, 1e-1, 100).

**Gen 11 evidence (exploit_2, controlled comparison on same starting array):**
- Broad (100 deltas, 1e-14 to 1e-1): 1917 improvements in 35s = 54.8/s
- Focused (40 deltas, 1e-14 to 1e-11): 3499 improvements in 35s = 100.0/s
- Focused also achieved better final C (by ~5e-12)

This confirms gen 10 exploit_1's observation that 99.6% of improvements come
from delta=1e-13 or smaller. Dead scales (1e-1 to 1e-12) waste 60% of trial
time for essentially 0% of improvements.

**Recommendation:** Use np.geomspace(1e-14, 1e-11, 30-40) as the standard
delta grid for all future CD runs on well-polished arrays.
