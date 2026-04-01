---
type: idea
id: idea_005
name: "Re-tune BLIS Tile Sizes for Tiger Lake"
lifecycle: active
confidence: 0.5
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 2
supported_by: [explore_1/sol10, gen002/experimentator_1/exp3]
contradicted_by: [explore_1/sol01, explore_1/sol06, gen002/exploit_1/sol04]
related_ideas: [idea_008, idea_019]
cluster: cluster_002
tags: [tiling, NC, MC, cache, blis]
---

Current baseline: MC=64, KC=128, NC=256 (tuned for AVX2). With AVX-512 (64-byte
wide ops), NC should be re-evaluated for the larger register width and Tiger Lake
cache hierarchy (L1d=48KB, L2=1.25MB).

Gen002 NC sweep data still stands. Gen003 did not produce new BLIS solutions
(all agents focused on row-streaming and vpshufb approaches). The BLIS approach
is at diminishing returns (pattern_007) and gen003's exploit_1 was explicitly
redirected to row-streaming.

**Staleness note:** Last confirmed in gen 2. With the shift to row-streaming
architecture (idea_014), BLIS tile tuning is becoming less relevant. The row-
streaming architecture doesn't use NC/MC tiling. However, BLIS remains competitive
(148.18 µs gen001) and may be relevant for hybrid approaches.

Confidence slightly lowered — the optimization focus has moved away from BLIS.
