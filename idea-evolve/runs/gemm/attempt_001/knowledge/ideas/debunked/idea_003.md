---
type: idea
id: idea_003
name: "VNNI for Accumulation"
lifecycle: debunked
confidence: 0.1
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 0
supported_by: []
contradicted_by: []
related_ideas: []
cluster: null
tags: [vnni, vpdpbusd, accumulation]
---

`_mm512_dpbusd_epi32` computes a dot product of int8 values and accumulates into
int32, all in one instruction (1 cycle throughput). The binary-ternary multiply
was hypothesized to be reformulatable as a VNNI operation.

Research agent (Finding 11) conclusively determined that VNNI does NOT apply to
bit-packed binary-ternary data. The ternary values {-1,0,+1} are stored as two
bit-planes (pos_bits, neg_bits), not as sign-magnitude integers. To use VNNI,
you'd need to decode bit-packed values back to integer form first (expand 8 bits
→ 8 × int8), and this decoding step costs more than the operation saves. The
popcount approach is inherently more efficient for bit-packed data.

No agent attempted a VNNI-based solution in gen001. Debunked based on theoretical
analysis — the data format mismatch is fundamental, not implementation-specific.
