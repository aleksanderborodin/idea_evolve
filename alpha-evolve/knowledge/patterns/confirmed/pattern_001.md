---
type: pattern
id: pattern_001
name: "Memset dominates large benchmark cost"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
evidence: [explore_1/sol07, explore_1/sol08, full_1/sol02, full_1/sol04]
related_ideas: [idea_010]
tags: [memset, memory-bandwidth, large-benchmark]
---

For the large benchmark (128×65536, C = 32 MB), `memset(C, 0, ...)` consumes
~1000-3500 µs — a substantial fraction of total execution time. Removing memset
(via direct stores) consistently provides 1.5-2x speedup on the large benchmark.

Evidence: explore_1/sol07 (with memset) scored 306.60 µs. explore_1/sol08 (memset
removed, otherwise identical) scored 178.28 µs — 1.72x faster. Similarly,
full_1/sol02 (339.09 µs, with memset for some paths) vs full_1/sol04 (167.23 µs,
memset skipped) shows a 2.03x improvement.

This pattern reveals that memory bandwidth, not compute, is the primary bottleneck
for the large benchmark. Any optimization that reduces memory traffic (fewer writes,
streaming stores, avoiding redundant reads) will disproportionately help large.
