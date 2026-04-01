---
type: pattern
id: pattern_011
name: "Row-streaming kernel is at a memory bandwidth wall — compute optimizations yield negligible benefit"
lifecycle: active
confidence: 0.85
first_seen: generation_3
last_updated: generation_3
evidence: [gen003/exploit_1/sol02, gen003/exploit_1/sol06, gen003/exploit_1/sol07, gen003/exploit_1/sol08, gen003/exploit_1/sol09, gen003/exploit_1/sol10, gen003/exploit_1/sol11, gen003/exploit_1/sol13]
related_ideas: [idea_014, idea_001, idea_011]
tags: [bandwidth, memory-bound, compute, diminishing-returns, wall]
---

Exploit_1 (gen003) tested 13 kernel variants, trying to optimize compute
(fewer instructions, better ILP, different math formulations). 12 of 13 regressed.
The single improvement (sol02, 141 µs) is likely from compiler code layout effects,
not compute changes.

Specific compute optimizations that failed:
- Inline A broadcast (sol08): 230 µs (+56%)
- Software prefetch (sol09): 254 µs (+73%)
- Single vpternlog math (sol10): 332 µs (+125%)
- __restrict__ pointers (sol11): 181 µs (+23%)
- Specialized fast path (sol13): 212 µs (+44%)
- #pragma GCC unroll (sol09): 254 µs (+73%)

The inner loop is ~7 instructions per k-byte with good ILP from two independent
vpternlog+popcnt chains. The compiler produces near-optimal code. The bottleneck
is DRAM bandwidth for B reads (L2 → registers) and C writes (registers → DRAM/L3).

**Implication for gen004:** Do not invest in compute kernel optimizations.
Focus exclusively on reducing memory traffic:
1. Multi-row B sharing (idea_022, 4-row)
2. NT stores for large (idea_021, 128-bit)
3. Multi-threading for bandwidth (idea_020)
4. Column-blocked output to reduce C write-back traffic
