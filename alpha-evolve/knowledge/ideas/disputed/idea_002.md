---
type: idea
id: idea_002
name: "Fully Unrolled k-Loop"
lifecycle: disputed
confidence: 0.4
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol09]
contradicted_by: [full_1/sol03]
related_ideas: [idea_008]
cluster: cluster_001
tags: [unrolling, k-loop, template-specialization]
---

k_bytes is always 2, 4, or 7 for our benchmark sizes. Instead of a generic loop,
create specialized versions for each k value via template specialization or
`switch(k_bytes)` dispatch.

Evidence is mixed from generation 1. full_1/sol03 used template specialization
with `switch(k_bytes)` dispatch to create 6 kernel variants (3 k values × 2 store
modes). This caused I-cache pressure from code bloat and *regressed* performance
(442.43 µs vs 339.09 µs for sol02 without templates). Small case degraded from
11.61 → 20.04 µs specifically.

However, explore_1/sol09 used `#pragma GCC unroll` (a lighter approach) and
achieved 171.04 µs. explore_1/sol10 also uses `#pragma GCC unroll 7` in its
micro-kernel and achieved the best score (148.18 µs).

Conclusion: compiler-hint unrolling (`#pragma`) works; heavy template
specialization with multiple kernel copies hurts via I-cache pressure. The idea
is partially valid but the implementation approach matters critically.
