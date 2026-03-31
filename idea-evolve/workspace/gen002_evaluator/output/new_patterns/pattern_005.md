---
type: pattern
id: pattern_005
name: "Medium benchmark is near memory bandwidth floor (~8% headroom)"
lifecycle: active
confidence: 0.8
first_seen: generation_2
last_updated: generation_2
evidence: [gen002/experimentator_1/exp4, gen002/explore_1/sol01]
related_ideas: [idea_006, idea_015]
tags: [bandwidth, medium-benchmark, floor, memory-bound]
---

The medium benchmark (64×16384, C = 4 MB) is already operating within ~8% of
its theoretical memory bandwidth floor. Experimentator_1 measured:
- Current best medium time: 228 µs
- Theoretical minimum (streaming stores at 18 GB/s for 4 MB): ~247 µs
- Regular store bandwidth at 4 MB: ~17 GB/s → floor ~247 µs

This means further optimization of medium is nearly impossible through compute
improvements alone. The bottleneck is DRAM write bandwidth, not computation.

Implication: to improve the geomean, agents should focus on:
1. Large benchmark (still 1.5x above bandwidth floor — NT stores can close this)
2. Small benchmark (10x above theoretical floor — dominated by overhead)
3. Accept that medium is approximately at its limit

Gen002 data supporting this: explore_1/sol01 achieved medium=225.55 µs, which
is essentially at the floor. No gen002 solution achieved medium below 220 µs.
