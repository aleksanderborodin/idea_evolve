---
type: idea
id: idea_008
name: "Singer q=101 Truncation with Cyclic Shifts"
lifecycle: established
confidence: 0.95
first_seen: generation_1
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002_exploit_1_sol01, gen002_exploit_1_sol02, gen002_exploit_1_sol03, gen002_exploit_2_sol02, gen002_exploit_2_sol03, gen002_exploit_2_sol04]
contradicted_by: []
related_ideas: [idea_006, idea_007, idea_004]
cluster: cluster_001
tags: [algebraic, singer, truncation, high-impact, confirmed]
---

The Singer set for q=101 has 102 elements in Z_{10303}. Since 10303 > 10000, not all elements
necessarily fit in {0, ..., 10000}. However, with the optimal cyclic shift, ALL 102 elements
fit in range — zero truncation loss.

**Generation 2 evidence**: exploit_1 implemented this and scored **102** (is_valid=1, violations=0).
The construction uses GF(101³) with irreducible cubic x³ - 3x - 1 and primitive element (0,0,2).
The optimal cyclic shift d=2337 places all 102 elements within {0, ..., 10000}. Confirmed
independently by exploit_2/sol02 (different shift selection method, same result).

**Key findings from gen 2**:
- 569 out of 10303 cyclic shifts (5.5%) preserve all 102 elements within range.
- 43.5% of shifts give ≥100 elements. The averaging argument mathematically guarantees
  ≥105 shifts give ≥100 elements (proved by research_1).
- All 1054 irreducible cubics over GF(101) give identical shift distributions (PGL equivalence).
- Singer q=103 (104 elements in Z_{10713}) gives at most 102 in range. q=107 gives 100. q=109 gives 98.
  q=101 is optimal for N=10000.
- Greedy extension from the 102-element truncated set adds 0 elements — the set is locally saturated.

**Status**: Upgraded from active to established. This is now the dominant construction, superseding
Singer q=97 perturbation (idea_007) for achieving the highest score.
