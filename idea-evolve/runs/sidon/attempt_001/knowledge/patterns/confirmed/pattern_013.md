---
type: pattern
id: pattern_013
name: "Beam search greedy ceiling at 70"
lifecycle: confirmed
confidence: 0.85
first_seen: generation_5
last_updated: generation_5
evidence: [gen005_explore_1_sol01, gen005_explore_1_sol02, gen005_explore_1_sol03, gen005_explore_1_sol04, gen005_explore_1_sol05, gen005_explore_1_sol06, gen005_explore_1_sol07]
related_ideas: [idea_021, idea_015, idea_016, idea_003]
tags: [beam-search, greedy, ceiling, non-algebraic]
---

Beam search with greedy candidate selection reaches exactly 70 elements for N=10000,
one more than standard greedy variants (69). The beam width saturates at k=500 — going
to k=800 produces identical results.

**Updated non-algebraic greedy hierarchy** (extends pattern_011):
- Random greedy: 58-63
- Standard greedy: 66
- LNS from greedy: 67
- SA from greedy: 68
- Fibonacci ordering: 69
- Min-blocking greedy: 69
- **Beam search k=500+: 70** (NEW)
- ET(71) + greedy + 1-opt: 75 (still best non-Singer)

**Key insight**: Diverse candidate sampling hurts (66 vs 70). The optimal single-step
policy is always "take the smallest valid candidate." Beam width compensates for
occasional bad choices in this greedy policy but cannot overcome the structural
limitation of ~70 elements for non-ET approaches.

This effectively closes the greedy research direction for Sidon sets at N=10000.
