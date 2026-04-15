---
type: idea
id: idea_007
name: "1-Opt Intensification"
lifecycle: active
confidence: 0.5
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_explore_2_sol01]
contradicted_by: []
related_ideas: [idea_006]
cluster: cluster_002
tags: [local-search, 1-opt, intensification, swap]
---

# 1-Opt Intensification

## What It Is

A local search intensification step applied after ILNS: for each codeword, try swapping it with two compatible codewords (2-for-1 swap) to potentially improve the solution.

## How It Works

1. Start from an ILNS solution
2. For each position `i` in the code:
   a. Find all pairs (c1, c2) of codewords compatible with each other AND with all other codewords
   b. If codeword `i` can be replaced by such a pair, do so
3. Repeat until no improvement found (max 10 iterations)

## Evidence

- Used in explore_2/sol01 after ILNS
- ILNS best was ~290, after 1-opt: no improvement reported
- The 1-opt step did not yield additional codewords in practice

## Current Performance

Carried on top of ILNS solution at ~290. No measurable improvement from the 1-opt step alone.

## When It Helps

For codes near a local optimum where a single codeword is blocking extension but a swap could open up space. Less effective when the bottleneck is the overall structure (as with ILNS on this problem).

## Limitations

- 2-for-1 swaps are rare when the code is already highly constrained
- Requires scanning all pairs of compatible candidates per position — O(n²) per position
- On M(8,5) with d=5, the compatibility graph is sparse, making good swap pairs rare
