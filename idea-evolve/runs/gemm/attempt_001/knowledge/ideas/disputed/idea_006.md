---
type: idea
id: idea_006
name: "Streaming Stores for Large m"
lifecycle: disputed
confidence: 0.4
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [full_1/sol02, full_1/sol04, gen002/experimentator_1/exp1b, gen003/exploit_1/sol02]
contradicted_by: [gen003/exploit_1/sol01, gen003/exploit_1/sol03, gen003/exploit_1/sol12, gen003/experimentator_1/sol01, gen003/experimentator_1/sol01b, gen003/explore_1/sol04]
related_ideas: [idea_010, idea_015, idea_021]
cluster: cluster_002
tags: [streaming-stores, non-temporal, memory-bandwidth, large-m, alignment]
---

For large C matrices (>8 MB), use `_mm512_stream_si512` to bypass cache on stores,
eliminating RFO (read-for-ownership) overhead and cache pollution.

**Gen003 results — extensively tested, mostly negative:**

1. **Aligned-buffer NT stores + memcpy back = DEFINITIVE FAILURE.**
   - Exploit_1/sol01: 513 µs (3.5x worse). memcpy from DRAM-cold NT buffer negates gains.
   - Experimentator_1/sol01: 400 µs (per-rep _mm_malloc, 8192 page faults).
   - Experimentator_1/sol01b: 251 µs (static BSS buffer, still DRAM-cold read issue).
   The aligned-buffer workaround is now thoroughly debunked.

2. **Unconditional NT stores on C = CRASH.** Exploit_1/sol12 confirmed C is NOT
   64-byte aligned for the correctness test (small allocations use heap, 16-byte aligned).

3. **Runtime alignment check = marginal benefit.** Exploit_1/sol02 (141.0 µs, new best):
   checks `C % 64 == 0` at runtime, uses NT stores only if aligned AND C > 8 MB. The
   4.3% improvement over baseline (147.26 µs) may partly be from the dead `if(use_nt)`
   branch changing compiler code layout, not from NT stores actually triggering.

4. **NT stores don't help sequential row-streaming writes.** Explore_1 tested NT stores
   on the 1-row kernel (sol04: 184.84 µs) — worse than without. The hardware prefetcher
   already handles RFO efficiently for sequential access patterns.

5. **XMM stream stores (16-byte aligned) = slight regression.** Exploit_1/sol03: 152 µs.
   Too many store instructions from 4× _mm_stream_si128 per 64-byte block.

**Confidence lowered from 0.7 to 0.4.** The standalone 2.3x measurement from gen002
does not translate to integrated kernel performance. NT stores remain theoretically
beneficial for large but practically blocked by alignment constraints and hardware
prefetcher efficiency.

**Remaining path:** research_1 proposed _mm_stream_si128 (SSE, 16-byte aligned) as
the correct fix — this bypasses the 64-byte alignment requirement. See idea_021.
