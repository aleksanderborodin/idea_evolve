---
type: cluster
id: cluster_002
name: "Search-Based and Non-Singer Methods"
member_ideas: [idea_001, idea_002, idea_003, idea_005, idea_011, idea_014, idea_015, idea_016, idea_021]
best_score: 75
best_solution: gen002_explore_1_sol03
status: exhausted
last_updated: generation_7
---

This cluster contains ideas based on search heuristics, ordering strategies, and
non-Singer algebraic constructions.

**Gen 7 consistency review update:**
- **idea_011 (ET Extension + Search) ARCHIVED**: 75-ceiling confirmed 6+ times across gens 2-7.
  30+ independent trials all converge to 75. Gen 7 confirmed Ruzsa-Lindstrom converges to
  same basin (pattern_018). Body stated "no further investment recommended." Now archived to
  match idea_003, idea_015, idea_016, idea_021 (all archived gen 6 at same evidence threshold).

**All member ideas now debunked or archived:**
- idea_001 (Randomized Greedy): debunked, 58-63
- idea_002 (Local Search/LNS): debunked, max +1 gain
- idea_003 (Difference-Aware): archived, ceiling 69
- idea_005 (Backtracking): debunked gen 6, 66
- idea_011 (ET Extension + Search): **archived gen 7**, ceiling 75 (hard)
- idea_014 (Probabilistic Alteration): debunked, 63
- idea_015 (Fibonacci Ordering): archived, ceiling 69
- idea_016 (Min-Blocking): archived, ceiling 69
- idea_021 (Beam Search): archived, ceiling 70

**Non-algebraic ceiling hierarchy (final):**
- Random greedy: 58-63
- Standard greedy: 66
- DFS/backtracking: 66
- LNS from greedy: 67
- SA from greedy: 68
- Fibonacci ordering: 69
- Min-blocking greedy: 69
- Beam search k=500+: 70
- ET(71) + greedy + 1-opt: **75** (hard ceiling, pattern_015)
- Ruzsa(71) + greedy + VLNS: **75** (same basin, pattern_018)

**Verdict**: Cluster exhausted. 30-element gap to algebraic best (105) is structural.
No remaining active ideas. No further exploration warranted.
