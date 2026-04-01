---
type: idea
id: idea_015
name: "Size-Adaptive NT Stores"
lifecycle: active
confidence: 0.4
first_seen: generation_2
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen002/experimentator_1/exp1b]
contradicted_by: [gen003/exploit_1/sol01, gen003/experimentator_1/sol01, gen003/experimentator_1/sol01b, gen003/explore_1/sol04]
related_ideas: [idea_006, idea_010, idea_021]
cluster: cluster_002
tags: [streaming-stores, non-temporal, size-adaptive, alignment]
---

Use non-temporal (streaming) stores for the C output matrix ONLY when the output
exceeds L3 cache size (~8 MB). For smaller outputs, use regular stores.

**Gen003 results — confidence lowered from 0.7 to 0.4:**

The gen002 estimated "2.3x on large" was measured on a standalone streaming write
benchmark, not an integrated kernel. In practice:

- Aligned-buffer + memcpy approach: **net negative** (memcpy from DRAM-cold buffer
  costs more than RFO savings). Tested by exploit_1/sol01 (513 µs), experimentator_1
  (400 µs and 251 µs). Thoroughly debunked.
- Direct NT stores to C: blocked by alignment constraint (correctness test C is
  16-byte aligned, not 64-byte). Confirmed by exploit_1/sol12 crash.
- Runtime alignment check: exploit_1/sol02 achieves 141 µs, but the improvement is
  suspected to come from compiler code layout changes, not NT stores actually firing.

**The medium regression is confirmed:** 4 MB fits in L3, and streaming stores bypass
useful cache. Multiple gen003 agents independently confirmed this.

**Remaining viable approach:** SSE 128-bit NT stores (_mm_stream_si128), which only
require 16-byte alignment. See idea_021. Research_1 estimated this could drop large
from 3841 µs to ~1350 µs, potentially achieving geomean ~105 µs.

The idea remains **active** because the size-adaptive principle is sound — the
implementation just needs 128-bit NT stores instead of 512-bit.
