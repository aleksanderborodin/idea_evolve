---
type: pattern
id: pattern_011
name: "All greedy variants ceiling at 66-70"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_3
last_updated: generation_5
evidence: [gen003_explore_2_sol05, gen004_explore_1_sol01, gen004_explore_2_sol01, gen005_explore_1_sol05, gen005_explore_1_sol07]
related_ideas: [idea_001, idea_003, idea_015, idea_016, idea_021]
tags: [greedy, ceiling, structural-limit]
---

All greedy-family approaches for Sidon set construction in {0, ..., 10000} converge to
a ceiling of 66-70 elements regardless of candidate selection strategy or beam width.

**Updated hierarchy (gen 5)**:
- Random greedy: 58-63
- Standard ascending greedy: 66
- LNS from greedy: 67
- SA from greedy: 68
- Fibonacci ordering: 69
- Min-blocking greedy: 69
- **Beam search k=500+: 70** (NEW gen 5 — ceiling confirmed, k=800 identical to k=500)

**Gen 5 update**: Beam search (idea_021) was the last untested greedy variant. It reaches
70, exactly 1 above the previous ceiling. The beam width saturates at k=500. This
conclusively establishes the greedy-family structural limit at ~70 for N=10000.

The 30+ element gap between greedy ceiling (70) and algebraic constructions (105) confirms
that fundamentally different approaches are needed for competitive scores.
