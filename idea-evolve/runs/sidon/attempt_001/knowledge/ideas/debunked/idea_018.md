---
type: idea
id: idea_018
name: "SA with Violation Relaxation"
lifecycle: debunked
confidence: 0.05
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_explore_2_sol06]
related_ideas: [idea_010, idea_002]
cluster: cluster_003
tags: [simulated-annealing, violations, relaxation, non-algebraic, debunked]
---

Standard SA for Sidon sets fails because the valid neighborhood is empty at local optima. Relaxed SA uses objective = |S| - penalty × violations, allowing temporary violations. After SA completes, extract the largest valid Sidon subset.

Generation 3 evidence: explore_2/sol06 applied this to the 68-element Fibonacci greedy set. Parameters: T=3.0, T_min=0.05, alpha=0.9998, penalty=8.0. After 58 seconds: **68** (no improvement). The SA never found a valid state with more than 68 elements.

Analysis: The swap neighborhood (remove 1, add 1) with violation relaxation is still too local. Moving through violated states requires coordinated multi-element rearrangements that random swaps almost never find. The penalty term prevents SA from exploring deeply violated states where structure might emerge.

Verdict: **Debunked.** Violation-relaxed SA doesn't help for non-algebraic sets either. Previously shown to fail for Singer seeds (idea_010); now confirmed to fail for search-found seeds too. The fundamental issue is that Sidon constraint satisfaction is too globally coupled for local swap neighborhoods, regardless of relaxation. This, combined with idea_010's debunking, closes the SA research direction entirely.
