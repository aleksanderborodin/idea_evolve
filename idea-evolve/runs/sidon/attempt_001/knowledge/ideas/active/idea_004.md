---
id: idea_004
type: idea
name: "int16 Accumulation"
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

The diff per byte (popcount_pos - popcount_neg) is at most ±8. For k_bytes ≤ 15,
the accumulated sum fits in int16 (max ±120). Accumulate in 16-bit, widen to 32-bit
only at the end. This doubles the number of elements processed per register.
