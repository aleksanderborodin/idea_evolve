---
type: pattern
id: pattern_012
name: "Coordinate descent convergence is exponentially decaying on TTT-Discover 30k"
lifecycle: active
confidence: 0.85
first_seen: generation_7
last_updated: generation_7
evidence: [gen005_exploit_2_sol01, gen006_exploit_1_sol01, gen007_exploit_1_sol01, gen007_exploit_2_sol01, gen007_full_1_sol04]
related_ideas: [idea_019, idea_021]
tags: [coordinate-descent, convergence, diminishing-returns, TTT-Discover]
---

Single-element coordinate descent on the TTT-Discover 30k array shows exponentially
decaying improvement rates across generations:

| Generation | Agent | Improvements | Delta C | Notes |
|---|---|---|---|---|
| Gen 5 | exploit_2 | 116 | -8.82e-9 | Top-500 by gradient, 10 passes |
| Gen 6 | exploit_1 | 14373 | -2.58e-8 | Full-array scan, major extension |
| Gen 7 | exploit_1 | 6551 | -9.96e-10 | Full-array, 6 rounds, converging |
| Gen 7 | exploit_2 | 156 | -2.13e-9 | 3 rounds, converged at 0 |
| Gen 7 | full_1/sol04 | 257 | -1.217e-9 | 2 rounds, converged |

Gen 6 exploit_1 reported "1800 improvements/round in round 3" and claimed "NOT converging."
Starting from that same output, gen 7 exploit_1 found rapid convergence: 2495 → 2306 →
1526 → 125 → 83 → 16 per round. 96.6% of improvements came in the first 3 rounds.

**The coordinate-wise optimum for single-element moves is essentially reached.** Further
improvement requires multi-element moves (triplet perturbation, idea_021) or fundamentally
different approaches (LP).
