---
type: cluster
id: cluster_002
name: "Search-Based and Non-Singer Methods"
member_ideas: [idea_001, idea_002, idea_003, idea_005, idea_011, idea_014, idea_015, idea_016, idea_021]
best_score: 75
best_solution: gen002_explore_1_sol03
status: exhausted
last_updated: generation_6
---

This cluster contains ideas based on search heuristics, ordering strategies, and
non-Singer algebraic constructions.

**Gen 6 — CLUSTER STATUS: EXHAUSTED**

Two critical updates:
1. **idea_005 (Backtracking) DEBUNKED**: First empirical test (explore_1/sol01) scored 66
   (greedy baseline). DFS IS greedy for sequential ordering. Randomized restarts also fail.
   After 6 generations untested, now definitively closed.
2. **75 ceiling confirmed as hard structural barrier** (pattern_015): ET(71)+1-opt tested
   with 2-opt, LNS (k=2-15), and 30+ randomized restarts. All converge to exactly 75.

**All member ideas are now debunked or at confirmed ceilings:**
- idea_001 (Randomized Greedy): debunked, 58-63
- idea_002 (Local Search/LNS): debunked, max +1 gain
- idea_003 (Difference-Aware): active but peripheral only, ceiling 69
- idea_005 (Backtracking): **debunked gen 6**, 66
- idea_011 (ET Extension + Search): active, ceiling 75 (hard)
- idea_014 (Probabilistic Alteration): debunked, 63
- idea_015 (Fibonacci Ordering): active, ceiling 69
- idea_016 (Min-Blocking): active, ceiling 69
- idea_021 (Beam Search): active, ceiling 70

**Non-algebraic ceiling hierarchy (final):**
- Random greedy: 58-63
- Standard greedy: 66
- DFS/backtracking: **66** (gen 6, NEW)
- LNS from greedy: 67
- SA from greedy: 68
- Fibonacci ordering: 69
- Min-blocking greedy: 69
- Beam search k=500+: 70
- ET(71) + greedy + 1-opt: **75** (hard ceiling confirmed gen 6)

**Verdict**: This cluster is exhausted. 35-element gap to algebraic best (105) is structural.
Only remaining speculative directions: SA from 75-element ET seed (not yet tried), or
C-implemented 2-opt. Neither is likely to bridge the 30-element gap.
