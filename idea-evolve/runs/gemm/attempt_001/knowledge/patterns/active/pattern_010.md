---
type: pattern
id: pattern_010
name: "C write scatter destroys multi-row kernel benefit"
lifecycle: active
confidence: 0.8
first_seen: generation_3
last_updated: generation_3
evidence: [gen003/exploit_1/sol04, gen003/exploit_1/sol05, gen003/explore_1/sol02, gen003/explore_2/sol04]
related_ideas: [idea_009, idea_016, idea_022]
tags: [C-write, scatter, multi-row, cache, locality]
---

Processing multiple rows per j-block (to share B loads) causes C write addresses
to scatter across distant memory locations. For the large benchmark (m=65536),
consecutive row writes are 256 KB apart.

**Gen003 evidence (4 independent data points):**

| Solution | Rows | Large (µs) | vs 1-row |
|----------|------|-----------|----------|
| exploit_1/sol04 | 8-row | 8013 | 2.1x worse |
| exploit_1/sol05 | 8-row | 8021 | 2.1x worse |
| explore_1/sol02 | 8-row | 3213 | 0.84x (better!) |
| explore_2/sol04 | 4-row | 5682 | vs 9470 (1.67x better) |

The pattern is nuanced: multi-row benefits large by reducing B loads, but hurts
small/medium where B is already cache-resident and the C scatter overhead dominates.

**8-row is too aggressive** — the C scatter penalty on small/medium outweighs B
savings. **4-row appears to be the sweet spot** — explore_2 showed consistent
1.55-1.67x improvement on medium/large with acceptable small regression.

**Key insight from exploit_1:** "Memory write locality > memory read reduction."
The 8-row kernel halves B loads but doubles the effective C write footprint per
j-block, overwhelming L1 capacity.

**Mitigation strategy:** Column-blocked output (process NC columns for all R rows
before advancing) could keep C tiles in L1 while preserving B sharing.
