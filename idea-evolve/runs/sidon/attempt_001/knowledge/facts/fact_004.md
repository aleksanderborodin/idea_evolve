---
id: fact_004
type: fact
name: "Violation Tolerance"
confidence: 0.8
first_seen: generation_0
verified: false
source: user-provided
tags: []
---

If a solution has violations (repeated pairwise sums), the validator extracts
the largest valid Sidon subset using a greedy algorithm. So submitting a
slightly-too-large set with a few violations can still score well — the
extracted subset may be larger than a perfectly valid smaller set.
