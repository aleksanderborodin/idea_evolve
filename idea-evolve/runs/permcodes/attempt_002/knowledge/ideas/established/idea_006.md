---
type: idea
id: idea_006
name: "Iterated Large Neighborhood Search (ILNS)"
lifecycle: established
confidence: 0.85
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_explore_2_sol01, gen001_explore_2_sol02, gen001_explore_2_sol05]
contradicted_by: []
related_ideas: [idea_005, idea_008, idea_009]
cluster: cluster_002
tags: [ILNS, local-search, stochastic, bucket, M(8,5)]
---

# Iterated Large Neighborhood Search (ILNS)

## What It Is

A stochastic local search combining greedy construction with large-neighborhood destruction and repair: repeatedly (1) destroy a fraction of the current code by removing random codewords, (2) greedily rebuild the code from the surviving ones, (3) accept improvements.

## How It Works

1. Greedy construction from random start → initial code
2. **Destroy**: Remove k% of codewords randomly (20-50% typical)
3. **Repair**: Greedily add compatible codewords to surviving ones
4. **Accept**: Keep new code if it improves; else keep old
5. Repeat steps 2-4 for many iterations/restarts

## Evidence

- sol01 (ILNS v1): 290 (8 restarts × 300 iters)
- sol02 (aggressive ILNS): 284 (20 restarts × 600 iters, larger destroy fractions)
- sol05 (fixed ILNS): 293 (15 restarts × 400 iters)
- All far below 616 from AGL orbit approach

## Current Performance

Best: **293** (sol05). Average: **289**. Evaluated in 60-384 seconds.

## When It Helps

ILNS can escape local optima that pure greedy gets stuck in (262 → 290-293 improvement). However, it cannot approach the orbit-based optimum of 616.

## Limitations

- ILNS without group structure is fundamentally limited
- The bucket structure (70 bucket IDs) provides efficient compatibility checking but not the right search space decomposition
- Best ILNS result (293) is less than half the gap between 262 (pure greedy) and 616 (AGL optimum)

## Relationship to VNS

VNS (idea_013, not yet tried) would systematically vary the destroy fraction across neighborhoods, potentially finding better solutions than random ILNS.
