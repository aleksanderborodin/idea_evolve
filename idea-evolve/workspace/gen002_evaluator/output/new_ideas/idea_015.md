---
type: idea
id: idea_015
name: "Size-Adaptive NT Stores"
lifecycle: active
confidence: 0.7
first_seen: generation_2
last_updated: generation_2
last_confirmed_gen: 2
supported_by: [gen002/experimentator_1/exp1b]
contradicted_by: []
related_ideas: [idea_006, idea_010]
cluster: cluster_002
tags: [streaming-stores, non-temporal, size-adaptive, alignment]
---

Use non-temporal (streaming) stores for the C output matrix ONLY when the
output exceeds L3 cache size (~8 MB). For smaller outputs, use regular stores.
This combines the best of both worlds: no cache pollution for large, full
cache benefit for small/medium.

Experimentator_1 (gen002) measured the impact precisely:
- Small (128 KB C): streaming 8.62 µs vs regular 9.47 µs → 1.1x (negligible)
- Medium (4 MB C): streaming 317.43 µs vs regular 298.89 µs → **0.9x (WORSE)**
- Large (32 MB C): streaming 4226.65 µs vs regular 9849.99 µs → **2.3x WIN**

The medium regression is because 4 MB fits in L3 (8 MB), and streaming stores
bypass useful cache. The large improvement is because 32 MB exceeds L3 and
regular stores cause RFO (read-for-ownership) doubling effective DRAM traffic.

**CRITICAL CONSTRAINT**: The benchmark harness allocates C with `std::vector<int>`,
which is NOT guaranteed to be 64-byte aligned. `_mm512_stream_si512` requires
64-byte alignment. Solutions must either:
1. Check alignment at runtime: `((uintptr_t)C % 64 == 0)`
2. Allocate an internal aligned buffer, compute with NT stores, then memcpy back

The runtime check is simpler but may never succeed depending on allocator
behavior. The internal buffer approach guarantees NT stores work but adds
memcpy overhead.

Research agent estimated that with NT stores for large, the geomean could drop
from ~148 µs to ~30-40 µs. This is the single highest-leverage optimization
remaining.

Decision logic:
```cpp
bool use_nt = ((size_t)n * m * 4 > 8*1024*1024) && ((uintptr_t)C % 64 == 0);
```
