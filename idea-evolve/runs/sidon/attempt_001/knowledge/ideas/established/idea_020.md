---
type: idea
id: idea_020
name: "Rokicki-Dogon Near-Optimal Golomb Rulers"
lifecycle: established
confidence: 0.95
first_seen: generation_4
last_updated: generation_6
last_confirmed_gen: 6
supported_by: [gen005_experimentator_1_sol01, gen005_experimentator_1_sol02, gen005_experimentator_1_sol03, gen005_research_1_sol01, gen005_research_1_sol02, gen006_exploit_1_sol01, gen006_full_1_sol01, gen006_full_1_sol02, gen006_full_1_sol03, gen006_full_1_sol04]
contradicted_by: []
related_ideas: [idea_006, idea_008, idea_022, idea_023]
cluster: cluster_001
tags: [literature, golomb-rulers, construction, high-impact, verified]
---

The Rokicki-Dogon "Possibly Optimal Golomb Rulers" database (cube20.org/golomb) contains
near-optimal Golomb ruler constructions (equivalent to Sidon sets) for various mark counts
and spans.

**Generation 5 — VERIFIED AND EXPLOITED**:
Both experimentator_1 and research_1 independently downloaded and parsed the database.
Key results:

| Marks | Span  | Type | q   | Multiplier | Fitness |
|-------|-------|------|-----|------------|---------|
| 105   | 9884  | ap   | 107 | 433        | **105** |
| 104   | 9581  | pp   | 103 | 400        | **104** |
| 103   | 9408  | pp   | 103 | 400        | **103** |
| 102   | 9218  | pp   | 101 | 1758       | 102     |

**Generation 6**: Used as baseline by exploit_1 (perturbation analysis) and full_1 (CP-SAT warm-start, VLNS). The 105-mark set's self-healing property (pattern_014) was discovered through Rokicki-Dogon data.

**Exhaustive search confirms 105 is the ceiling** from this database for N=10000.

**Gen 6 consistency fix**: last_confirmed_gen updated to 6. Added gen 6 solutions to supported_by.
