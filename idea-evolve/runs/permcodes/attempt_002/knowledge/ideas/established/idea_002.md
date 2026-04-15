---
type: idea
id: idea_002
name: "Degree-Ordered Greedy Clique Selection"
lifecycle: established
confidence: 0.9
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_explore_1_sol01, gen001_explore_1_sol03, gen001_explore_1_sol02]
contradicted_by: []
related_ideas: [idea_001, idea_005]
cluster: cluster_001
tags: [greedy, clique, heuristic, vertex-ordering]
---

# Degree-Ordered Greedy Clique Selection

## What It Is

A greedy algorithm for maximum clique: start from a seed vertex, iteratively add the vertex with the most neighbors among remaining candidates. The "degree-ordered" variant sorts candidates by their degree within the candidate set (not global degree) at each step.

## How It Works

1. Start with a seed vertex `v`
2. Candidate set = neighbors of `v`
3. While candidates exist: pick vertex `u` in candidates with highest degree within candidates; add to clique; update candidates to intersection of neighbors
4. Return clique

## Evidence

- Used in all AGL orbit clique solutions (6/6 at 616)
- Confirmed as optimal for the AGL orbit graph by exhaustive 720-vertex search
- Consistent regardless of starting vertex (all produce same 11-orbit result)

## Performance

Best score: **616** (as part of AGL orbit clique). Alone (on full permutation graph): **262** as direct greedy.

## When It Helps

On the AGL orbit graph, greedy finds the global optimum. On the full 40320-vertex permutation graph, greedy gets trapped in local optima (262 vs 616). The orbit structure is key — it eliminates many equivalent permutations, making greedy effective.

## Relationship to Other Ideas

This is the standard greedy for clique construction. It works well when the graph has a regular structure (as the AGL orbit graph does). For the full permutation graph, it performs poorly.
