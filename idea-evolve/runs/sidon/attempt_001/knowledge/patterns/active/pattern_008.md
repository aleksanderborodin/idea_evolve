---
type: pattern
id: pattern_008
name: "Non-algebraic search methods ceiling at 69 for N=10000"
lifecycle: active
confidence: 0.8
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_explore_2_sol01, gen003_explore_2_sol02, gen003_explore_2_sol03, gen003_explore_2_sol04, gen003_explore_2_sol05, gen003_explore_2_sol06, gen003_explore_1_sol01]
related_ideas: [idea_001, idea_002, idea_015, idea_018]
tags: [ceiling, non-algebraic, search, landscape]
---

Generation 3 thoroughly explored non-algebraic search methods:

| Method | Best Score | Trials |
|--------|-----------|--------|
| Randomized greedy restarts | 63 | 25s worth |
| Probabilistic alteration | 63 | 160 configs |
| LNS from greedy-66 | 67 | 24s LNS |
| Spread-first greedy + LNS | 65 | multiple restarts |
| Fibonacci ordering greedy | 69 | 2400+ params |
| SA with violation relaxation | 68 | 58s |

The hierarchy is clear:
- Random greedy: 58-63
- Standard greedy: 66
- LNS from greedy: 67
- Fibonacci ordering: 68-69
- SA from Fibonacci: 68 (no improvement)

The 69-element ceiling appears hard. 2400+ Fibonacci parameters found only one configuration
reaching 69. LNS and SA cannot improve beyond the greedy-optimal for their seed.

The gap from 69 (search ceiling) to 102 (Singer) is 33 elements — confirming that algebraic
construction quality dominates over search refinement by a factor of ~1.5x.
