---
id: cluster_001
name: "AVX-512 Micro-Kernel Compute"
status: active
best_score: 141.0
best_solution: gen003/exploit_1/sol02
member_ideas: [idea_001, idea_002, idea_004, idea_007, idea_009, idea_011, idea_016, idea_022]
last_updated: generation_3
---

# Cluster 001 — AVX-512 Micro-Kernel Compute

This cluster covers ideas related to the compute core of the GEMM kernel:
instruction selection, accumulation strategy, register usage, and micro-kernel
geometry.

## Member Ideas

- **idea_001** (established, 0.95) — AVX-512 popcount: foundational, all solutions use it
- **idea_002** (disputed, 0.4) — k-loop unrolling: pragma works, template hurts
- **idea_004** (established, 0.95) — int8/int16 deferred widening: universal in top solutions
- **idea_007** (established, 0.85) — vectorized pack_B: BLIS-path only, less relevant with row-streaming
- **idea_009** (active, 0.5) — 8-row kernel: register pressure solved by int8, but C write scatter is new problem
- **idea_011** (active, 0.75) — vpternlogd fused logic: used by 12+ solutions, likely beneficial
- **idea_016** (active, 0.6) — 8-row int8 kernel: first empirical result 168 µs, C scatter limits benefit
- **idea_022** (active, 0.6) — 4-row B-amortization: sweet spot between 1-row and 8-row, 1.55-1.67x on med/large

**Removed:** idea_018 (vpshufb LUT) — debunked in gen003. 2.3x worse than popcnt kernel due to port 5 contention.

## Key Findings

The compute kernel itself is at a memory bandwidth wall (pattern_011). Port 5
bottleneck is from vpbroadcastb (fact_008), not vpopcntb as previously thought.
The 4-row B-amortization (idea_022) is the most promising compute-side improvement,
but has not yet been tested with the winning ternlogd+popcnt kernel.

## Status

Active. The cluster's best score (141.0 µs) is the overall best. Future gains
are more likely from memory-side optimizations (cluster_002) than compute-side,
but the 4-row kernel variant remains untested with the correct compute path.
