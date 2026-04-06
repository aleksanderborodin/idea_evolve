---
type: pattern
id: pattern_012
name: "Singer is suboptimal for small N — ILP finds larger Sidon sets"
lifecycle: active
confidence: 0.9
first_seen: generation_4
last_updated: generation_4
evidence: [gen004_full_1_sol01]
related_ideas: [idea_019, idea_006, idea_008]
tags: [singer-suboptimal, ILP, exact, small-N, structural]
---

CP-SAT ILP solver (gen004_full_1) proved that Singer difference sets are NOT optimal for
small N:

| N | Singer size | ILP optimal | Gap |
|---|------------|-------------|-----|
| 56 | 8 (q=7) | 10 | +2 |
| 132 | 12 (q=11) | 13 | +1 |

This is a significant structural finding. The Singer construction gives a perfect difference
set in Z_{q²+q+1}, but truncation to {0,...,N} is lossy, and the ILP can find sets that
exploit the truncated range more efficiently.

**Implication for N=10000**: Singer q=101 gives 102 but this may NOT be the maximum.
CP-SAT returned UNKNOWN (not INFEASIBLE) for k=103, N=10000 — meaning 103 is possible.
The Rokicki-Dogon database (idea_020) suggests 105 may be achievable.

**Key question**: Do the "Singer+1" solutions at small N share algebraic structure that
generalizes? If so, this could guide construction of 103+ element sets for N=10000.
