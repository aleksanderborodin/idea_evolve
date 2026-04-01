---
type: pattern
id: pattern_009
name: "Compiler code layout sensitivity — dead branches can improve performance"
lifecycle: active
confidence: 0.5
first_seen: generation_3
last_updated: generation_3
evidence: [gen003/exploit_1/sol02]
related_ideas: [idea_006, idea_015]
tags: [compiler, code-layout, fragile, optimization]
---

Exploit_1/sol02 achieved 141.0 µs (4.3% improvement over 147.26 µs baseline)
with a runtime NT store check that likely **never triggers**. The agent reported:
"Sol02's improvement appears to come from the dead `if(use_nt)` branch changing
compiler code layout for small/medium."

The `if (use_nt)` branch adds ~20 instructions of dead code (NT store path) that
shifts the alignment of the hot loop's instruction addresses. On modern x86, loop
alignment affects instruction fetch bandwidth and µop cache (DSB) hit rates.

**Implication:** Sub-5% performance differences in this problem may be noise from
compiler code layout rather than genuine algorithmic improvements. A/B testing
should use >30% threshold for reliable signal (explore_1 reported 30-40% variance
between runs of the same solution).

This is a fragile, non-reproducible optimization that depends on exact compiler
version and optimization passes. It should not be chased intentionally, but
agents should be aware that small regressions after code changes may be layout
effects, not algorithmic problems.
