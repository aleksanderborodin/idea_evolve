---
type: idea
id: idea_005
name: "Fast Compatibility Mask (23x Speedup)"
lifecycle: established
confidence: 1.0
first_seen: gen001
last_updated: gen001
last_confirmed_gen: gen001
supported_by: [architect_report_gen001]
contradicted_by: []
related_ideas: [idea_003, idea_006]
cluster: search_heuristics
tags: [performance, optimization, helper, compatibility-graph]
---

`helpers.compat.fast_compatible_mask` computes which permutations are compatible with a partial code in O(1) per check via bit-vector representation. The architect noted this is 23x faster than brute force scanning all 40320 permutations.

Critical for ILS, tabu search, and simulated annealing — all iterative agents that need to evaluate many candidate additions per iteration. Without this helper, iterative search is prohibitively slow.

Should be used by all solution agents doing iterative improvement.
