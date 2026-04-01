---
id: idea_003
type: idea
name: "VNNI for Accumulation"
lifecycle: active
confidence: 0.3
first_seen: generation_0
last_updated: generation_0
last_confirmed_gen: 0
supported_by: []
contradicted_by: []
related_ideas: []
cluster: null
tags: []
---

`_mm512_dpbusd_epi32` computes a dot product of int8 values and accumulates into
int32, all in one instruction (1 cycle throughput). The binary-ternary multiply
might be reformulatable as a VNNI operation since element values are {-1,0,+1}
and {-1,+1}. This could eliminate the popcount step entirely.
