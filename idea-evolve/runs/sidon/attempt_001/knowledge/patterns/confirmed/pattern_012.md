---
type: pattern
id: pattern_012
name: "105 is the algebraic ceiling for N=10000"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_5
last_updated: generation_5
evidence: [gen005_experimentator_1_sol01, gen005_experimentator_1_sol02, gen005_experimentator_1_sol03, gen005_research_1_sol01, gen005_research_1_sol02]
related_ideas: [idea_022, idea_023, idea_006, idea_008, idea_020]
tags: [ceiling, algebraic, construction, boundary]
---

Exhaustive search across all algebraic construction types (Singer/projective plane,
Bose-Chowla/affine plane) and all prime powers q ≤ 109, with exhaustive multiplier
search for each, confirms that **105 marks is the maximum achievable by known algebraic
constructions for N=10000**.

**Evidence**:
- Best 105: Bose-Chowla q=107, mul=433, span=9884 (fits)
- Best 104: Singer q=103, mul=400, span=9581 (fits)
- Best 106: Singer q=107, mul=best, span=10135 (DOES NOT FIT, 135 over)
- Tested: pp q=107 (9072 multipliers), ap q=107 (~5700), pp q=109 (~9900)
- All 106+ mark constructions have span > 10000

**Constructive hierarchy for N=10000**:
| Marks | Span  | Construction        | Fits? |
|-------|-------|---------------------|-------|
| 102   | 9218  | Singer pp q=101     | YES   |
| 103   | 9408  | Singer pp q=103     | YES   |
| 104   | 9581  | Singer pp q=103     | YES   |
| 105   | 9884  | Bose-Chowla ap q=107| YES   |
| 106   | 10135 | Singer pp q=107     | NO    |

**Implication**: The remaining gap from 105 to the upper bound (~109-114) must be
closed by computational search methods (CP-SAT, backtracking, ILP), not algebraic
construction. This is the most important strategic insight from generation 5.
