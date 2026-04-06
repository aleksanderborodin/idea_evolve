---
id: idea_003
type: idea
name: "Difference-Aware Construction"
lifecycle: active
confidence: 0.35
first_seen: generation_0
last_updated: generation_4
last_confirmed_gen: 4
supported_by: [gen004_explore_2_sol01]
contradicted_by: []
related_ideas: [idea_005, idea_016, idea_015]
cluster: cluster_002
tags: [construction, difference-aware, heuristic, greedy-variant]
---

Instead of checking violations after the fact, maintain the set of used differences explicitly. When choosing the next element to add, pick one that uses "rare" differences (large gaps in the difference spectrum). This leaves more room for future elements.

Used peripherally in several solutions and now centrally tested via idea_016 (min-blocking greedy). Gen 4 confirmed that the corrected min-blocking implementation achieves 69 elements — identical to the Fibonacci ordering ceiling (idea_015). The concept has practical value but does not break the non-algebraic greedy ceiling of ~69.

**Gen 4 addition**: explore_2 also tested Ruzsa quadratic construction φ(x) = x*p + (x² mod p) and CRT product construction. Both FAILED: Ruzsa had violations in integers (valid only in Z_p × Z_p), CRT had cross-term collision issues. These are NOT viable difference-aware constructions.

May be more useful as a subroutine within ILP or beam search formulations rather than as a standalone greedy heuristic.
