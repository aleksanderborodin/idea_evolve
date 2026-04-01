---
type: idea
id: idea_021
name: "SSE 128-bit NT Stores (_mm_stream_si128)"
lifecycle: active
confidence: 0.5
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: []
contradicted_by: []
related_ideas: [idea_006, idea_015]
cluster: cluster_002
tags: [streaming-stores, sse, 128-bit, alignment, non-temporal]
---

Use `_mm_stream_si128` (SSE, 128-bit) instead of `_mm512_stream_si512` (AVX-512,
512-bit) for non-temporal stores. The key advantage: SSE NT stores only require
16-byte alignment, which `std::vector<int>` satisfies on glibc x86_64.

**Proposed by research_1 (gen003)** as the correct fix for the alignment constraint
(fact_006) that has blocked all 512-bit NT store approaches.

**Expected impact (from research_1 analysis):**
- Large: 3841 µs → ~1350 µs (bandwidth ceiling with streaming writes)
- Medium: no change (regular stores, C fits in L3)
- Small: no change (regular stores)
- Geomean: ~105 µs (from 141 µs)

**Consistency review note (gen003):** The previous `contradicted_by` entry
(exploit_1/sol03, 152 µs) has been removed. Sol03 used 4× _mm_stream_si128
**unconditionally for ALL sizes**, which is a different configuration than the
proposed size-adaptive approach (NT only for large). The medium regression from
unconditional NT stores dragged sol03's geomean down. The specific proposed
configuration — SSE 128-bit NT stores applied ONLY to large — has **never been
tested** and remains the highest-priority experiment for gen004.

**Implementation:**
```cpp
// Replace per 64 bytes of C output:
// From: _mm512_storeu_si512(dst, acc32_0..3);  // 4 zmm stores
// To (when large):
_mm_stream_si128((__m128i*)(dst+0),  _mm512_castsi512_si128(acc32_0));
_mm_stream_si128((__m128i*)(dst+4),  _mm512_extracti32x4_epi32(acc32_0, 1));
// ... 16 total _mm_stream_si128 for 64 bytes
```

**Risk:** 16 SSE stores vs 4 ZMM stores per 64 bytes = 4x more store instructions.
This may cause store port saturation. Needs empirical evaluation.

**HIGHEST PRIORITY experiment for gen004.** This is the most promising path to
breaking below 100 µs.
