---
type: pattern
id: pattern_002
name: "NC=256 consistently outperforms NC=512 for 4x64 kernel"
lifecycle: active
confidence: 0.7
first_seen: generation_1
last_updated: generation_1
evidence: [explore_1/sol01, explore_1/sol02, explore_1/sol06, explore_1/sol10, full_1/sol04]
related_ideas: [idea_005]
tags: [tiling, NC, cache, performance]
---

Solutions using NC=256 consistently outperform those using NC=512, despite NC=512
theoretically reducing the number of B-panel packing operations. Examples:
- explore_1/sol02 (NC=256): 400.68 µs vs explore_1/sol01 (NC=512): 654.75 µs
- explore_1/sol10 (NC=256): 148.18 µs vs full_1/sol04 (NC=512): 167.23 µs
- explore_1/sol06 (NC=512 with direct stores): 465.65 µs

The root cause is unclear. Hypotheses from explore_1: cache line conflicts, TLB
pressure, B panel alignment issues. The B panel at NC=512 is 512 × k_bytes bytes
(max 3584 bytes for k=7), which still fits in L1. The regression may be due to
micro-kernel call overhead patterns or cache set conflicts rather than capacity.

This pattern suggests NC=256 is near-optimal for the current 4×64 micro-kernel
shape on Tiger Lake, and larger NC values should be explored cautiously.
