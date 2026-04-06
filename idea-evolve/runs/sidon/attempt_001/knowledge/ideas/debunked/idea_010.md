---
type: idea
id: idea_010
name: "Simulated Annealing from Algebraic Seed"
lifecycle: debunked
confidence: 0.1
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 2
supported_by: []
contradicted_by: [gen002_exploit_2_sol01, gen002_exploit_2_sol03, gen003_explore_2_sol06]
related_ideas: [idea_002, idea_006, idea_007, idea_008, idea_018]
cluster: cluster_003
tags: [hybrid, simulated-annealing, search, debunked]
---

Use a high-quality algebraic seed as the starting point for simulated annealing, allowing
temporary size reductions to explore the fitness landscape beyond local optima.

**Generation 2 evidence**: Two SA runs from Singer seeds: SA from 99-element q=97 perturbation
(114s, ~500K iterations, no improvement) and SA from 102-element q=101 truncation (114s,
Boltzmann acceptance, no improvement).

**Generation 3 evidence**: explore_2/sol06 tested SA with violation relaxation (objective =
size - 8*violations) from a 68-element Fibonacci greedy set. 58 seconds, no improvement.
This extends the SA failure to non-algebraic seeds — SA fails not just because Singer sets
are saturated, but because the Sidon constraint landscape fundamentally resists local search.

**Verdict**: Downgraded to debunked. SA has been tried:
1. From Singer q=97 seed (99 elements) — fails
2. From Singer q=101 seed (102 elements) — fails
3. From Fibonacci greedy seed (68 elements) — fails
4. With standard SA and violation-relaxed SA — both fail

Three generations of evidence with zero improvement across all seed types and SA variants.
The swap neighborhood is structurally disconnected for Sidon sets at sizes >60.
