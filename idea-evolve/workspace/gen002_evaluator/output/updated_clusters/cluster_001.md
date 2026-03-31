---
type: cluster
id: cluster_001
name: "AVX-512 Micro-Kernel Compute"
member_ideas: [idea_001, idea_002, idea_004, idea_007, idea_009, idea_011, idea_016, idea_018]
best_score: 147.26
best_solution: gen002/explore_1/sol01
status: active
last_updated: generation_2
---

This cluster groups ideas related to the AVX-512 micro-kernel's compute path:
hardware popcount (idea_001), k-loop unrolling (idea_002), accumulation strategy
(idea_004), SIMD packing (idea_007), kernel width (idea_009), fused boolean
logic via vpternlogd (idea_011), 8-row int8 kernel (idea_016), and vpshufb LUT
kernel (idea_018).

The best solution using this cluster is gen002/explore_1/sol01 at 147.26 µs
(5.23x baseline). Note: this solution uses a row-streaming architecture
(cluster_003) rather than BLIS, but still depends on the core AVX-512 compute
ideas from this cluster.

**Gen002 findings:**
- Experimentator_1 confirmed int8 accumulation gives 11-13% improvement (idea_004)
- Port 5 bottleneck identified from int16 widening ops (pattern_008)
- 8-row int8 kernel (idea_016) is theoretically sound but untested empirically
- Exploit_1 tried 12 BLIS variants, none improved — diminishing returns (pattern_007)

**Next frontier for this cluster:**
- 8-row int8 kernel (idea_016) — highest priority after NT stores
- vpshufb LUT kernel (idea_018) — alternative compute path to relieve port 5
- Combine int8 accum + 8-row with NT stores for synergistic gains
