---
type: idea
id: idea_005
name: "Direct Greedy on Full Permutation Space"
lifecycle: established
confidence: 0.9
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_explore_1_sol04]
contradicted_by: []
related_ideas: [idea_002, idea_006]
cluster: cluster_002
tags: [greedy, full-space, baseline, 40320-vertices]
---

# Direct Greedy on Full Permutation Space

## What It Is

Apply greedy clique construction directly to the full 40320-vertex permutation graph, without using orbit decomposition. Use random starting vertices and random ordering to explore different greedy trajectories.

## How It Works

1. Enumerate all 40320 permutations of {0,...,7}
2. Start from random permutation, greedily add compatible ones
3. Repeat from multiple random starting points
4. Keep the best code found

## Evidence

- explore_1/sol04: 50 random restarts → **262** codewords
- This is only **43%** of the 616 AGL-orbit result
- Strong evidence that orbit structure captures essential combinatorial properties

## Current Performance

**262** (best of 50 restarts). Evaluated in 55.7 seconds.

## When It Helps

As a baseline to measure the value of algebraic structure. The 262 baseline shows that without orbit decomposition, greedy is severely suboptimal.

## Key Insight

The gap between 262 (direct greedy) and 616 (orbit clique) shows that the AGL orbit decomposition provides enormous search space reduction. 720 vertices vs 40320 — a 56x reduction in search space that doesn't lose any optimal solutions (for this group action).

## Relationship to ILNS

ILNS approaches (290-293) do better than raw greedy (262) but still far below 616. The bucket-based compatibility checking helps, but not enough to overcome the lack of algebraic structure.
