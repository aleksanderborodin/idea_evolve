---
type: cluster
id: cluster_003
name: "Alternative Architectures (Non-BLIS)"
member_ideas: [idea_014]
best_score: 141.0
best_solution: gen003/exploit_1/sol02
status: active
last_updated: generation_3
---

This cluster groups ideas about fundamentally different kernel architectures
that do not follow the BLIS packing/tiling template. Contains idea_014 (row-
streaming no-pack architecture), now **established** (promoted from active).

**Gen003 established this as the dominant architecture.** The row-streaming
approach produced the new overall best: **141.0 µs** (exploit_1/sol02), improving
over gen002's 147.26 µs. All gen003 solutions scoring under 250 µs use row-streaming.

**Key gen003 discovery: the architecture is memory-bandwidth-bound.**
Three agents independently concluded that compute optimizations yield negligible
benefit because DRAM bandwidth for C writes and B reads is the bottleneck
(pattern_011). This is the most important strategic finding of gen003.

The row-streaming architecture has clear advantages for the next optimization
frontier (memory bandwidth reduction):
- Sequential C writes enable NT stores (once alignment is solved)
- Simple loop structure enables multi-threading (split rows across cores)
- No packing overhead means B bandwidth reduction from multi-row sharing
  directly improves overall performance

The cluster may expand if fundamentally different approaches emerge (e.g.,
output-stationary architecture, blocked output with register tiling).
