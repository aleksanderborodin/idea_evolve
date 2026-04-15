---
type: idea
id: idea_009
name: "Tabu-Style Diversification"
lifecycle: active
confidence: 0.4
first_seen: gen_01
last_updated: gen_01
last_confirmed_gen: gen_01
supported_by: [gen001_explore_2_sol02]
contradicted_by: []
related_ideas: [idea_006]
cluster: cluster_002
tags: [tabu, diversification, ILNS, local-search]
---

# Tabu-Style Diversification

## What It Is

A diversification strategy for ILNS that avoids revisiting recently removed codewords. When destroying a fraction of the code, track which codewords were removed and temporarily exclude them from rebuild candidates.

## How It Works

1. Keep a "tabu list" of recently removed codewords
2. When destroying k% of codewords, add removed ones to tabu list
3. When rebuilding, exclude tabu-listed codewords from candidates
4. Periodically clear tabu list to allow re-exploration

## Evidence

- Used in explore_2/sol02 (aggressive ILNS v2)
- Result: **284** (worse than non-tabu ILNS at 290-293)
- The tabu approach did not help in this case

## Current Performance

**284** (used in aggressive ILNS, which performed worse than simpler ILNS)

## When It Helps

When the search is cycling through the same solutions repeatedly. Tabu can force exploration of different regions.

## Limitations

- For this problem, ILNS already explores enough — tabu overhead didn't pay off
- The aggressive ILNS (with tabu) used 20 restarts × 600 iters but still worse than simpler ILNS
- May need tuning of tabu tenure and acceptance criteria
