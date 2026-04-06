---
type: pattern
id: pattern_005
name: "Singer q=101 is optimal prime for N=10000"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_2
last_updated: generation_2
evidence: [gen002_exploit_1_sol01, gen002_exploit_2_sol02, gen002_exploit_2_sol04]
related_ideas: [idea_008, idea_006]
tags: [singer, optimization, prime-selection]
---

Among all Singer constructions for different primes q, q=101 maximizes the number of
elements achievable in {0, ..., 10000}:

| q   | Singer size | v = q²+q+1 | Best in {0,...,10000} |
|-----|-------------|------------|----------------------|
| 97  | 98          | 9507       | 98 (all fit)         |
| 101 | 102         | 10303      | **102** (all fit!)   |
| 103 | 104         | 10713      | 102                  |
| 107 | 108         | 11557      | 100                  |
| 109 | 110         | 11991      | 98                   |

q=101 hits the sweet spot: v=10303 is only 3% larger than 10001, so the best cyclic
shift can fit all 102 elements. Larger primes have v much greater than N, causing
truncation loss that exceeds the extra elements gained.

This was confirmed exhaustively by exploit_1 (tested all 1054 irreducible cubics for q=101,
all primes q=97 through q=109). 102 is the Singer ceiling for N=10000.
