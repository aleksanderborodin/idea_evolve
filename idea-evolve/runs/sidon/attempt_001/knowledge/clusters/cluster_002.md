---
type: cluster
id: cluster_002
name: "Search-Based and Non-Singer Methods"
member_ideas: [idea_001, idea_002, idea_003, idea_005, idea_011, idea_014, idea_015, idea_016]
best_score: 75
best_solution: gen002_explore_1_sol03
status: active
last_updated: generation_4
---

This cluster contains ideas based on search heuristics, ordering strategies, and
non-Singer algebraic constructions.

**Gen 4 changes**:
- **idea_016 (Min-Blocking Greedy) CONFIRMED**: Two independent implementations (explore_1: 68,
  explore_2: 69) confirm the corrected min-blocking greedy achieves 69 — same ceiling as
  Fibonacci ordering. The gen 3 broken implementation (280K violations) is now superseded.
- **pattern_011 ADDED**: All greedy variants confirmed to ceiling at 66-69 regardless of
  selection heuristic. This is a structural limit of the greedy paradigm.
- **Ruzsa and CRT constructions DEBUNKED**: explore_2 tested Ruzsa φ(x)=x*p+(x²%p) and
  CRT products — both produce violations in integers. Not viable.

**Updated hierarchy of non-algebraic ceilings** (unchanged from gen 3):
- Random greedy: 58-63
- Standard greedy: 66
- LNS from greedy: 67
- SA from greedy: 68
- Fibonacci ordering: 69
- Min-blocking greedy: 69 (NEW — same ceiling)
- ET(71) + greedy + 1-opt: 75 (still best non-Singer result)
- Singer q=101: 102

**Verdict**: No further greedy variant exploration recommended. Beam search (suggested by
both explore agents) is the only untested search method with theoretical potential to
exceed 75. ILP (cluster_004) is the primary path forward.
