---
type: idea
id: idea_016
name: "Min-Blocking Greedy (Difference-Aware Candidate Selection)"
lifecycle: active
confidence: 0.5
first_seen: generation_3
last_updated: generation_4
last_confirmed_gen: 4
supported_by: [gen004_explore_2_sol01, gen004_explore_1_sol01]
contradicted_by: []
related_ideas: [idea_003, idea_005, idea_015]
cluster: cluster_002
tags: [greedy, blocking, difference-aware, confirmed-ceiling-69]
---

At each greedy step, instead of picking the smallest valid candidate, pick the candidate
that would block the fewest OTHER valid candidates. "Blocking" means: adding c creates new
differences d = |c - s| for each s in S. Each such d blocks candidates c+d and c-d. Choose
the c that minimizes total newly blocked candidates.

**Generation 3 evidence**: explore_1/sol02 implemented this with a critical bug (did not
block midpoints). Produced 775 elements with 280,849 violations → fitness 0.

**Generation 4 evidence — CORRECTED IMPLEMENTATION**:
- explore_2/sol01: Correct min-blocking greedy with midpoint blocking. Score: **69**.
  Time: 19.6s. Valid Sidon set.
- explore_1/sol01: Numpy-vectorized version with duplicate bug (valid_arr[chosen] not cleared).
  Score: **68**. Time: 0.6s. Valid but slightly lower due to the bug.

**Key finding**: Corrected min-blocking greedy achieves 69 — the SAME ceiling as Fibonacci
ordering greedy (idea_015). This confirms that the 69-element ceiling for non-algebraic
greedy methods is structural, not an artifact of any particular candidate selection heuristic.
All greedy variants (ascending, Fibonacci, min-blocking, spread-first) converge to 66-69.

**Ceiling**: 69 for N=10000. Further optimization of the blocking heuristic is unlikely to
exceed 70. The greedy approach is fundamentally limited regardless of selection strategy.
