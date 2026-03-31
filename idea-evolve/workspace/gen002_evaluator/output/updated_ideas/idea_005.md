---
type: idea
id: idea_005
name: "Re-tune BLIS Tile Sizes for Tiger Lake"
lifecycle: active
confidence: 0.6
first_seen: generation_0
last_updated: generation_2
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

**Gen002 NC sweep data (experimentator_1):**

| NC | small (µs) | medium (µs) | large (µs) | geomean (µs) |
|----|-----------|------------|-----------|-------------|
| 64 | 10.80 | 592.43 | 7280.11 | 359.79 |
| 128 | 10.82 | **472.15** | 8106.31 | **345.94** |
| 192 | 12.27 | 685.55 | 7370.59 | 395.76 |
| 256 | 11.59 | 597.55 | 7333.52 | 370.29 |
| 384 | 10.98 | 571.93 | 8266.46 | 373.02 |
| 512 | 11.70 | 554.93 | 7604.11 | 366.83 |
| m | 12.65 | 629.60 | **6782.99** | — |

Key findings:
- **NC=128 is geomean winner** (345.94 µs), beating NC=256 (370.29 µs)
- Medium strongly prefers NC=128 (472 vs 597 µs for NC=256)
- Large prefers NC=m (no tiling) or NC=256. NC=128 hurts large (8106 µs)
- Small is relatively insensitive to NC

Gen002 exploit_1 tested NC=128 directly: sol04 got 274.11 µs (worse than
sol10's 148.18 µs with NC=256). The regression was attributed to more pack_A
calls for large sizes.

The optimal NC is **size-dependent** — see idea_019 for adaptive NC proposal.
NC=256 remains the best single value when large benchmark matters, but NC=128
is strictly better for medium-dominated workloads.

Confidence raised slightly based on comprehensive NC sweep data. MC=64 and
KC=k_bytes remain uncontested.
