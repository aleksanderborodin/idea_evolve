---
type: pattern
id: pattern_008
name: "Port 5 bottleneck from int16 widening ops dominates micro-kernel throughput"
lifecycle: active
confidence: 0.7
first_seen: generation_2
last_updated: generation_2
evidence: [gen002/experimentator_1/exp2]
related_ideas: [idea_004, idea_016]
tags: [port-5, widening, assembly, throughput, bottleneck]
---

Experimentator_1 inspected the compiled assembly of the best solution's
micro-kernel and identified a port 5 throughput bottleneck:

Per k-iteration (4 unrolled), port 5 uops breakdown:
- vpbroadcastb: 8 (port 5 only)
- vpmovsxbw: 8 (port 5 only — int8→int16 widening)
- vextracti32x8: 4 (port 5 only — extract upper half for int16)
- vpternlogq, vpaddw: ~4-8 (shared port 0/5)

Total: minimum 20 port 5 uops per k-iteration, likely 24-28 with shared ops.

The int16 widening operations (vpmovsxbw + vextracti32x8) account for 12 out
of 20+ port 5 uops — approximately 40% of port 5 pressure.

Switching to int8 accumulation eliminates ALL 12 widening uops from the inner
loop (they move to the post-k-loop widening step, executed only once). This
reduces port 5 pressure by ~40% in the hot path.

No register spills detected in the current 4-row int16 kernel (18 zmm used of
32 available). The kernel is throughput-limited, not latency- or register-limited.

This pattern directly motivates idea_016 (8-row int8 kernel): with port 5
freed up, the broadcast ops for 8 rows become affordable.
