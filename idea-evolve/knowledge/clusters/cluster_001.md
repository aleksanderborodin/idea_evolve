---
type: cluster
id: cluster_001
name: "AVX-512 Micro-Kernel Compute"
member_ideas: [idea_001, idea_002, idea_004, idea_007, idea_009, idea_011]
best_score: 148.18
best_solution: explore_1/sol10
status: active
last_updated: generation_1
---

This cluster groups ideas related to the AVX-512 micro-kernel's compute path:
hardware popcount (idea_001), k-loop unrolling (idea_002), accumulation strategy
(idea_004), SIMD packing (idea_007), kernel width (idea_009), and fused boolean
logic via vpternlogd (idea_011).

The best solution using this cluster is explore_1/sol10 at 148.18 µs (5.20x
baseline). Key established techniques: AVX-512 popcount (idea_001), deferred
widening in int16 (idea_004), vectorized pack_B (idea_007). Disputed: 8-row
kernel (idea_009) and heavy template unrolling (idea_002). Active: vpternlogd
(idea_011).

**Next frontier for this cluster:**
- Isolate vpternlogd contribution (idea_011)
- Retry 8-row kernel with int8 accumulation (idea_009 + idea_004)
- Test 6-row kernel as a middle ground
- Software prefetching for B panels
