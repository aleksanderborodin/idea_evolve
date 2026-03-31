---
type: pattern
id: pattern_006
name: "Kernel+store dominates at 93-95% of total time; packing is negligible"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_2
last_updated: generation_2
evidence: [gen002/experimentator_1/exp1]
related_ideas: [idea_007, idea_013, idea_014]
tags: [timing, phase-breakdown, kernel, packing, bottleneck]
---

Experimentator_1 performed the first per-phase timing breakdown of the best
solution (sol10, 148.18 µs):

| Phase | small (µs) | % | medium (µs) | % | large (µs) | % |
|-------|-----------|---|------------|---|-----------|---|
| pack_B | 0.13 | 1.1% | 2.29 | 0.5% | 15.75 | 0.3% |
| pack_A | 0.68 | 5.7% | 25.69 | 6.1% | 215.13 | 4.7% |
| kernel+store | 11.10 | 93.2% | 390.72 | 93.3% | 4350.71 | 95.0% |

Key findings:
- pack_B is essentially free (<1% of total)
- pack_A is minor (5-6% of total)
- Kernel + C store dominates at 93-95%

This has critical implications:
1. Eliminating packing (idea_013) saves <7% at most — far less than expected
2. The row-streaming no-pack approach (idea_014) achieves similar scores NOT
   because packing is expensive, but because the overhead is elsewhere
3. All optimization effort should target the micro-kernel compute path and
   the C store path (especially NT stores for large)
4. The explore_2 agent's hypothesis that "packing cost is negligible" is
   confirmed by direct measurement

For small specifically, pack_A accounts for 5.7% (0.68 µs). Eliminating it
could save ~0.5-0.7 µs — relevant only for pushing small below 3 µs.
