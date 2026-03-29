---
type: pattern
id: pattern_016
name: "FFT padding has zero effect on C computation (validated)"
lifecycle: confirmed
confidence: 0.99
first_seen: generation_8
last_updated: generation_8
evidence: [gen008_explore_2_observations]
related_ideas: [idea_019, idea_021, idea_022]
tags: [FFT, padding, numerical, validation, precision]
---

All FFT padding sizes (2N-1, 2N, next_pow2, 4N) produce identical C values to
within 1e-15 for the TTT-Discover 30k array. The -1e-8 to -1e-9 improvements
from coordinate descent, triplet perturbation, and quadruplet perturbation are
REAL, not FFT artifacts.

**Evidence (gen 8 explore_2):**

| Padding config     | C value          | diff from 2N reference |
|-------------------|------------------|----------------------|
| 2N (validate.py)  | 1.50286286889246 | reference            |
| 2N-1 (tight)      | 1.50286286889245 | ~1e-15               |
| next_pow2 (≥ 2N)  | 1.50286286889246 | identical            |
| 4N                | 1.50286286889246 | identical            |

**Why:** The N=30k solution has support mainly on a small portion of the domain.
The autoconvolution maximum is well within the linear convolution range regardless
of padding size. FFT aliasing does not affect the max_conv computation.

**Significance:** This closes the open question flagged by the system critic in
gen 5. All micro-optimization results since gen 5 are numerically trustworthy.
Promoted directly to confirmed lifecycle due to definitive experimental evidence.
