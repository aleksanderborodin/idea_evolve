---
type: idea
id: idea_004
name: "Randomized Perturbation Search"
lifecycle: established
confidence: 0.7
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_explore_1_sol03]
contradicted_by: []
related_ideas: [idea_001, idea_006]
cluster: cluster_002
tags: [perturbation, local-search, escape-local-optima]
---

# Randomized Perturbation Search

## What It Is

A local search technique that escapes local optima by randomly perturbing the current solution: remove 1-3 random orbits/codewords, then re-run greedy extension from the remaining ones. Repeating many times searches the neighborhood around the current optimum.

## How It Works

1. Start with a known clique (e.g., 11-orbit clique = 616)
2. Randomly remove 1-3 vertices
3. Run greedy extension from the remaining vertices
4. If better clique found, keep it; otherwise try again
5. Iterate 500+ times

## Evidence

- explore_1/sol03 ran 500 perturbation iterations
- Result: **616** (no improvement found)
- Suggests the 11-orbit AGL clique is a very strong local optimum — perturbation cannot escape it

## Current Performance

**616** (no improvement over baseline). All 500 perturbations converged back to the same 11-orbit clique.

## When It Helps

When the search space has multiple basins of attraction and greedy alone gets stuck. In the AGL orbit graph, there appears to be only one basin (the 11-orbit optimum), so perturbation finds nothing new.

## Limitations

- Limited by the structure of the orbit graph
- 500 iterations × 720-vertex graph = tractable but not exhaustive
- Would need to try different group decompositions to find different basins
