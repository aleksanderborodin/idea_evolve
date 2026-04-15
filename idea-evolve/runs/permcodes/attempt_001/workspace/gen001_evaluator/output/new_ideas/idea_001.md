---
type: idea
id: idea_001
name: "Greedy Nearest-Neighbor Construction"
lifecycle: established
confidence: 0.9
first_seen: gen000
last_updated: gen001
last_confirmed_gen: gen000
supported_by: [gen000_baseline_sol01]
contradicted_by: []
related_ideas: [idea_002, idea_003]
cluster: null
tags: [greedy, heuristic, baseline]
---

The simplest approach: start with one permutation and greedily add permutations that maintain the minimum distance constraint d=5. Multiple random restarts help find better starting points.

The gen000 baseline uses 20 random restarts over all 40320 permutations and achieves score 262. This is far below the 616 known bound, confirming that greedy alone is insufficient. The approach is O(K × N × d) where K is code size and N is number of candidates.

Time cost: 22 seconds for 20 restarts scanning all 40320 permutations. The bottleneck is checking distance against all existing codewords at each step.
