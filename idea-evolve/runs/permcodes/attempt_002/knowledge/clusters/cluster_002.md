---
type: cluster
id: cluster_002
name: "Stochastic Search"
lifecycle: established
confidence: 0.75
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
members: [idea_004, idea_005, idea_006, idea_007, idea_009, idea_010]
best_score: 293
tags: [stochastic, ILNS, greedy, local-search]
---

# Cluster: Stochastic Search

## Description

Search methods that operate on the full 40320-permutation space without algebraic orbit decomposition. All are fundamentally limited compared to algebraic approaches.

## Evidence

- Direct greedy: 262 (baseline)
- ILNS: 284-293 (best across 3 attempts)
- Perturbation search: 616 (no improvement over AGL baseline)
- GA crossover: INVALID (operator bug)

## Membership

- idea_004: Randomized perturbation search (established, confidence 0.7)
- idea_005: Direct greedy on full permutation space (established, confidence 0.9)
- idea_006: ILNS (established, confidence 0.85)
- idea_007: 1-opt intensification (active, confidence 0.5)
- idea_009: Tabu diversification (active, confidence 0.4)
- idea_010: GA crossover (disputed, confidence 0.2)

## Performance

Best score: **293** (ILNS). Average across valid attempts: ~289. All approaches cap far below 616 algebraic optimum.

## Exhausted?

**Partially.** ILNS has been tuned (v1, v2, v3) with diminishing returns. GA is broken. 1-opt and tabu are minor variations that didn't help. VNS and SA are unexplored variants that might do slightly better but cannot approach 616 without algebraic structure.

## For Gen 2

These methods should be deprioritized. If PGL orbit clique succeeds, stochastic methods become useful for extending a larger algebraic base. If PGL fails, we need exact methods (branch-and-bound) rather than more stochastic tuning.
