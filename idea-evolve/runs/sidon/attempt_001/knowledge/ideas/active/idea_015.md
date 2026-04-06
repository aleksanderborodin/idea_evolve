---
type: idea
id: idea_015
name: "Fibonacci/Exponential Ordering Greedy"
lifecycle: active
confidence: 0.5
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen003_explore_2_sol05]
contradicted_by: []
related_ideas: [idea_001, idea_003]
cluster: cluster_002
tags: [ordering, fibonacci, greedy, non-algebraic, moderate-gain]
---

Use Fibonacci-like sequences (a, b, a+b, a+2b, ...) or geometric sequences as the
candidate ordering for greedy Sidon construction, rather than ascending order or random
order. The exponential growth property of Fibonacci numbers naturally produces differences
that grow rapidly, reducing collision probability.

**Generation 3 evidence**: explore_2 searched 2400+ Fibonacci parameter pairs (a in [0,39],
b in [a+1, a+59]) plus geometric sequences (bases 1.3-3.0) and the Wythoff sequence.

Key results:
- Standard ascending greedy: 66
- Random-order greedy: 58-62 (worse)
- Fibonacci ordering fib(3,13): 68
- Wide Fibonacci search: **69** (new non-algebraic record)
- Geometric orderings: similar to ascending (66)
- Wythoff sequence (floor(k*phi)): 66 (no improvement)

**Insight**: The critical property is EXPONENTIAL GROWTH, not the specific ratio. Fibonacci
sequences grow exponentially (phi^k), which spaces early elements to minimize difference
collisions. The golden ratio itself doesn't help (Wythoff = 66). The gain is small (+3 over
greedy) but consistent and reproducible.

**Ceiling**: Appears to be 69 for N=10000 based on 2400+ trials. Further search unlikely
to yield 70+. The LNS post-processing on the 69-element set gave no improvement.

**Use case**: Best non-algebraic baseline. Useful for diversity but not competitive with
Singer (102).
