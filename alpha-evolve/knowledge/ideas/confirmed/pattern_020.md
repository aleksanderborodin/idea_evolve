---
type: pattern
id: pattern_020
name: "Ultra-fine CD fully subsumes multi-element integral-preserving perturbations"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_9
last_updated: generation_10
evidence: [gen009_exploit_1_sol01, gen010_explore_1_sol01, gen010_explore_2_sol01, gen010_exploit_2_sol01]
related_ideas: [idea_019, idea_021, idea_022, idea_023]
tags: [coordinate-descent, ultra-fine, triplet, quadruplet, minimax, subsumption, confirmed]
---

After ultra-fine coordinate descent (deltas down to 1e-11+), ALL integral-preserving
multi-element perturbations find zero improvements. This is now CONFIRMED with very
high confidence based on gen 10's comprehensive testing.

**Gen 10 evidence (4 independent confirmations):**

| Agent | Multi-element method | Trials | Improvements |
|---|---|---|---|
| explore_1 | Minimax LP triplets (K=28, idea_023) | 47,233 | 0 |
| explore_1 | Minimax LP quadruplets (K=28) | 21,217 | 0 |
| explore_2 | Standard triplets (3 strategies) | 200,000 | 0 |
| explore_2 | Standard quadruplets | 50,000 | 0 |
| exploit_2 | Standard triplets (A/B test) | ~27,000 | 0 |
| exploit_2 | Standard quadruplets (A/B test) | ~3,000 | 0 |

**Total: ~348,000 multi-element trials across 4 agents, 0 improvements.**

**Gen 9 evidence (prior):** exploit_1 found 0 triplet/quadruplet improvements after
ultra-fine CD (gen 9). explore_1 found 0 quadruplet improvements.

**PROMOTED TO CONFIRMED (from active).** The evidence is now overwhelming:
- 6+ independent sessions across 2 generations
- 3 different multi-element approaches (standard, momentum, minimax LP)
- ~400,000 total trials with zero positive results
- Theoretical explanation: minimax LP proves the solution is locally optimal for
  integral-preserving moves (origin is in convex hull of plateau gradient vectors)

**The interleaving protocol (pattern_014) is obsolete.** The recommended protocol is
now: ultra-fine CD only, with geometric delta spacing and FFT resync.
