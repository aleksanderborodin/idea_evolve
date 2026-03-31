---
type: pattern
id: pattern_003
name: "Template specialization causes I-cache pressure and regressions"
lifecycle: active
confidence: 0.7
first_seen: generation_1
last_updated: generation_1
evidence: [full_1/sol03, explore_1/sol10]
related_ideas: [idea_002]
tags: [template, i-cache, code-bloat, unrolling]
---

Heavy template specialization (multiple kernel variants instantiated via
`switch(k_bytes)` dispatch) hurts performance due to instruction cache pressure.
full_1/sol03 created 6 kernel copies (3 k_bytes × 2 store modes) and regressed
from 339.09 µs (sol02) to 442.43 µs. The small benchmark was hit hardest:
11.61 → 20.04 µs.

In contrast, lightweight compiler hints (`#pragma GCC unroll 7`) achieve loop
unrolling without code duplication. explore_1/sol10 uses this approach and
achieves 148.18 µs — the best score.

This pattern suggests: for this problem's small k values, let the compiler handle
unrolling via pragmas rather than manually instantiating multiple kernel templates.
The k-loop body is small enough that the compiler can unroll it efficiently.
