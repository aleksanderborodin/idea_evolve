---
type: pattern
id: pattern_011
name: "All greedy heuristics converge to 66-69 ceiling regardless of selection strategy"
lifecycle: active
confidence: 0.85
first_seen: generation_4
last_updated: generation_4
evidence: [gen004_explore_1_sol01, gen004_explore_2_sol01, gen003_explore_2_sol05, gen003_explore_2_sol03, gen003_explore_2_sol04]
related_ideas: [idea_016, idea_015, idea_003, idea_001]
tags: [ceiling, greedy, structural-limit]
---

Generation 4 confirmed that min-blocking greedy (idea_016, corrected) achieves 69 elements —
identical to the Fibonacci ordering ceiling (idea_015). Combined with prior generations:

| Greedy Variant | Best Score | Evidence |
|----------------|-----------|---------|
| Ascending (standard) | 66 | gen 1-3, many trials |
| Descending | 66 | gen 4 explore_2 |
| Random ordering | 58-63 | gen 1, 3 |
| Fibonacci ordering | 69 | gen 3 (2400+ params) |
| Min-blocking greedy | 69 | gen 4 (corrected impl) |
| Spread-first greedy | 65 | gen 3 |
| LNS from greedy seed | 67 | gen 3 |

The ceiling of 66-69 for all non-algebraic greedy methods is structural. The selection
heuristic (ascending, Fibonacci, min-blocking, spread-first) changes the exact score by
±3 but cannot break past ~69. This is likely a fundamental property of the greedy paradigm
for Sidon sets at N=10000.

**Implication**: No further greedy variants should be explored. To exceed 69, agents must
use algebraic constructions (Singer, ET) or exact methods (ILP/CP-SAT).
