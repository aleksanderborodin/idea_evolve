---
type: idea
id: idea_011
name: "Multi-Seed Clique Search"
lifecycle: established
confidence: 0.9
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_full_1_sol03]
contradicted_by: []
related_ideas: [idea_001, idea_002]
cluster: cluster_001
tags: [clique, exhaustive, greedy, orbit, verification]
---

# Multi-Seed Clique Search

## What It Is

Run greedy max-clique search from many different starting vertices/orderings to increase confidence that the global optimum has been found. If all starts converge to the same clique size, that size is likely the maximum.

## How It Works

1. Generate multiple starting orderings (random shuffles of vertices)
2. Run greedy clique from each starting point
3. Track the best clique size found across all starts
4. If best size is consistent across starts, it's likely optimal

## Evidence

- full_1/sol03: 500 different orderings → all produce exactly 11 orbits (616)
- explore_1/sol01: all 720 starting vertices → all produce 11 orbits (616)
- Very strong evidence that 11 is the maximum clique size in the AGL orbit graph

## Current Performance

**616** (as confirmation of AGL orbit clique optimality). Used as a verification strategy, not a new solving approach.

## When It Helps

When you need empirical confidence that a greedy solution is optimal. Running many seeds is cheap (seconds) and provides strong evidence.

## Key Insight

The AGL orbit graph has extremely regular structure — greedy is not getting stuck in local optima, it is finding the global optimum consistently. This is unusual for greedy on combinatorial graphs and suggests the graph has a special structure (possibly the regular degree = 138 property).

## Implications

If 11 orbits is the maximum clique in the AGL orbit graph, then improving beyond 616 requires a different group action (PGL, PSL) — not deeper search in the AGL structure.
