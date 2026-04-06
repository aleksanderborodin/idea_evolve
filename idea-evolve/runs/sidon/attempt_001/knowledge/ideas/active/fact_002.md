---
id: fact_002
type: fact
name: "Theoretical Upper Bound"
confidence: 0.95
first_seen: generation_0
last_updated: generation_4
verified: true
source: "Carter, Hunter, O'Bryant 2025; confirmed by research_1 gen 1, research_1 gen 2, research_1 gen 4"
tags: [upper-bound, theory]
---

For a Sidon set in {0, ..., N}, the maximum size is at most sqrt(N) + O(N^{1/4}).
For N=10000, the best known upper bound is approximately **109** (Carter, Hunter,
O'Bryant 2025).

**Current best achieved: 102** (Singer q=101 truncation, gen 2). Gap to bound: 7 elements.

Singer constructions cannot exceed 102 for N=10000. Reaching 103-109 requires
non-Singer methods or fundamentally different approaches (ILP, Rokicki-Dogon database).

**WARNING**: Previous version of this fact (in facts/ directory, generation 0) stated the
upper bound as "~100-102". This was WRONG and has been corrected. The theoretical bound
is ~109, not ~102. Agents must not treat 102 as near-optimal.
