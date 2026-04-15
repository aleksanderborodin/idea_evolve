---
type: pattern
id: pattern_003
name: "Stochastic methods cap far below algebraic optimum"
lifecycle: active
confidence: 0.95
first_seen: gen_01
last_updated: gen_01
evidence: [gen001_explore_1_sol04, gen001_explore_2_sol01, gen001_explore_2_sol02, gen001_explore_2_sol05]
related_ideas: [idea_005, idea_006, idea_010]
tags: [ILNS, GA, stochastic, structure, limitation]
---

# Stochastic Methods Cap Far Below Algebraic Optimum

## Pattern Description

Pure stochastic approaches (direct greedy, ILNS, GA) on the full 40320-permutation space achieve at best 293 codewords, compared to 616 from algebraic (AGL orbit clique) methods. The gap is 323 codewords — stochastic methods achieve only 47% of the algebraic optimum.

## Evidence

| Approach | Score | % of 616 |
|---------|-------|----------|
| Direct greedy (50 restarts) | 262 | 43% |
| ILNS v1 | 290 | 47% |
| Aggressive ILNS v2 | 284 | 46% |
| Fixed ILNS v3 | 293 | 48% |
| GA (failed) | 0 | 0% |
| AGL orbit clique | 616 | 100% |

## Key Insight

The bucket structure (70 bucket IDs) provides a 23x speedup but not the right search space decomposition. The AGL orbit reduction from 40320 vertices to 720 is lossless for the optimum — stochastic methods cannot replicate this reduction without the group structure.

## Implications

To beat 616, the system MUST explore different group actions (PGL, PSL) or exact methods (branch-and-bound, IP/LP). More ILNS/GA tuning on the full space will not close the gap.
