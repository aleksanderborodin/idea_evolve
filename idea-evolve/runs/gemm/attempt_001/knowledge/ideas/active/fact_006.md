---
type: fact
id: fact_006
name: "C Allocation Alignment in Benchmark Harness"
confidence: 0.9
first_seen: generation_2
verified: true
source: "experimentator_1 code inspection of std::vector<int> usage in bench_harness.cpp"
tags: [alignment, benchmark, streaming-stores, harness]
---

The benchmark harness allocates the output matrix C using `std::vector<int>`,
which is NOT guaranteed to be 64-byte aligned. Standard C++ allocators typically
provide 16-byte alignment (or sometimes 32-byte on some systems).

This has critical implications for streaming NT stores (`_mm512_stream_si512`),
which require 64-byte aligned addresses. Using them on unaligned addresses
causes a segfault.

Solutions must check alignment at runtime:
```cpp
bool can_stream = ((uintptr_t)C % 64 == 0);
```

Alternatives:
1. Allocate an internal aligned buffer, compute with NT stores, memcpy back
2. Use `_mm512_storeu_si512` (unaligned regular stores) as fallback
3. Request the harness be modified to use aligned allocation

Note: even with unaligned C base, store addresses within the BLIS loop may be
aligned if NC and MC are multiples of 16 (64 bytes / 4 bytes per int). But
the base address alignment is not guaranteed.
