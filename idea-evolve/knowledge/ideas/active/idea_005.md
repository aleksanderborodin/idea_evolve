---
type: idea
id: idea_005
name: "Re-tune BLIS Tile Sizes for Tiger Lake"
lifecycle: active
confidence: 0.5
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol10]
contradicted_by: [explore_1/sol01, explore_1/sol06]
related_ideas: [idea_008]
cluster: cluster_002
tags: [tiling, NC, MC, cache, blis]
---

Current baseline: MC=64, KC=128, NC=256 (tuned for AVX2). With AVX-512 (64-byte
wide ops), NC should be re-evaluated for the larger register width and Tiger Lake
cache hierarchy (L1d=48KB, L2=1.25MB).

Gen001 evidence is mixed on NC specifically:
- NC=256 is used by the best solutions (explore_1/sol10: 148.18 µs, explore_1/sol07: 306.60 µs)
- NC=512 consistently regressed: explore_1/sol01 (654.75 µs), explore_1/sol06 (465.65 µs),
  full_1/sol04 uses NC=512 but achieves 167.23 µs (good but worse than NC=256 sol10)
- NC=256 appears optimal for the current 4×64 micro-kernel shape

The reason NC=512 hurts is not yet fully understood. Hypotheses from explore_1:
cache line conflicts, TLB pressure, B panel alignment issues. Research agent
calculated that even NC=65536 (entire m) would fit B in L2 for the large benchmark.
The bottleneck may be pack_B overhead or cache associativity conflicts, not capacity.

MC=64 is used by all successful solutions and appears appropriate. KC tiling is
irrelevant (see idea_008). NC tuning remains an open optimization opportunity.
