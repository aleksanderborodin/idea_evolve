---
type: idea
id: idea_019
name: "Adaptive NC per Benchmark Size"
lifecycle: active
confidence: 0.5
first_seen: generation_2
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002/experimentator_1/exp3]
contradicted_by: []
related_ideas: [idea_005]
cluster: cluster_002
tags: [tiling, NC, adaptive, size-dependent]
---

Use different NC values depending on the output matrix size, rather than a
fixed NC for all sizes. Experimentator_1's NC sweep data shows the optimal NC
differs per benchmark size:

| NC | small (µs) | medium (µs) | large (µs) | geomean (µs) |
|----|-----------|------------|-----------|-------------|
| 64 | 10.80 | 592.43 | 7280.11 | 359.79 |
| 128 | 10.82 | **472.15** | 8106.31 | **345.94** |
| 192 | 12.27 | 685.55 | 7370.59 | 395.76 |
| 256 | 11.59 | 597.55 | 7333.52 | 370.29 |
| 512 | 11.70 | 554.93 | 7604.11 | 366.83 |
| m | 12.65 | 629.60 | **6782.99** | — |

Key observations:
- Medium strongly prefers NC=128 (B panel = 512 bytes fits in L1)
- Large prefers no tiling (NC=m) or large NC values
- Small is relatively insensitive to NC
- NC=128 wins geomean but hurts large by 10% vs NC=256

Decision logic:
```cpp
int nc = (m <= 16384) ? 128 : 256;  // or even m for large
```

This simple runtime dispatch could improve medium by ~20% (472 vs 597 µs)
while maintaining large performance. Combined with other optimizations,
this could contribute meaningfully to the geomean.

Note: experimentator_1's NC sweep was done with a specific kernel (not the
overall best solution), so absolute numbers differ from population best.
Relative trends should hold.
