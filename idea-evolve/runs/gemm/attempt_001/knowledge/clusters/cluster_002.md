---
type: cluster
id: cluster_002
name: "Memory & Tiling Optimization"
member_ideas: [idea_005, idea_006, idea_008, idea_010, idea_012, idea_015, idea_017, idea_019, idea_020, idea_021]
best_score: 141.0
best_solution: gen003/exploit_1/sol02
status: active
last_updated: generation_3
---

This cluster groups ideas about memory access patterns, buffer management, and
tiling strategy. **idea_013 (no-pack direct) moved to archived** — superseded
by idea_014 (row-streaming). **New: idea_020 (multi-threading), idea_021 (SSE
128-bit NT stores).**

**Gen003 key findings:**

1. **NT stores via aligned buffer + memcpy: DEFINITIVELY FAILED.** Tested 5 times
   by 3 agents (exploit_1, experimentator_1, explore_1). Memcpy from DRAM-cold
   NT buffer always costs more than the RFO savings. Dead end.

2. **Direct 512-bit NT stores: BLOCKED by alignment.** Confirmed by exploit_1/sol12
   crash. Correctness test C is 16-byte aligned, not 64-byte.

3. **SSE 128-bit NT stores (idea_021) proposed** as the correct alignment fix.
   Only requires 16-byte alignment. Exploit_1/sol03 partially tested this (152 µs)
   but applied unconditionally — size-adaptive version untested.

4. **Multi-threading (idea_020) identified** by research_1. cgexec has 2 cores.
   Pthreads could give 1.3-1.8x bandwidth improvement on large.

5. **idea_006 confidence lowered to 0.4.** Standalone 2.3x doesn't translate to
   integrated kernel due to hardware prefetcher already handling sequential RFO.

**Next frontier:**
- SSE 128-bit NT stores, size-adaptive (idea_021) — HIGHEST PRIORITY
- Multi-threading for bandwidth doubling (idea_020) — HIGH PRIORITY
- idea_005 (BLIS tile tuning) becoming stale — row-streaming doesn't use tiling
