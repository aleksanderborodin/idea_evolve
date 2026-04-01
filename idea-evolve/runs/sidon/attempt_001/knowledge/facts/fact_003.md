---
id: fact_003
type: fact
name: "Evaluation Speed"
confidence: 0.8
first_seen: generation_0
verified: false
source: user-provided
tags: []
---

evaluate.py runs in under 1 second for sets of ~100 elements. The bottleneck is
the O(n^2) pairwise sum check in validate.py. Agents can iterate quickly.
