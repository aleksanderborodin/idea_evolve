---
type: idea
id: idea_014
name: "Probabilistic Alteration (Random Sample + Repair)"
lifecycle: debunked
confidence: 0.05
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_explore_1_sol01]
related_ideas: [idea_001, idea_002]
cluster: cluster_002
tags: [probabilistic, alteration, random-sampling, non-algebraic, debunked]
---

Sample a random subset of {0, ..., N} with probability p per element, then iteratively remove the element with the highest violation count until the set is valid Sidon. Finally, greedily extend with remaining elements in shuffled order. Run many seeds and probabilities to find the best result.

Generation 3 evidence: explore_1/sol01 tested 160 configurations (4 probabilities × 40 seeds). Best result: **63 elements** (p≈0.013). This is significantly worse than deterministic greedy (66) and much worse than Singer (102).

Analysis: The random sampling starts with ~130 elements (p=0.013 × 10001) but must remove ~67 to achieve validity. The repair phase is destructive — each removal cascades into worsening the set. The greedy extension recovers ~30 elements but cannot compensate.

Verdict: **Debunked.** This approach is fundamentally weaker than structured greedy because it starts from a random, violation-heavy state. The repair phase destroys any accidental structure. Scoring 63 — below even the greedy baseline of 66 — confirms this is not a viable direction.
