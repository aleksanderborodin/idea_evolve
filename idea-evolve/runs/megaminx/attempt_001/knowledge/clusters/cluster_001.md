---
type: cluster
id: cluster_001
name: Compression baseline
member_ideas: [idea_001, idea_002, idea_005]
best_score: 46312
best_solution: gen001_explore_1_sol01
status: active
last_updated: gen_001
---

# Cluster: Compression Baseline

Compression approaches operate on the sample_submission paths directly, removing redundant move sequences without search. These approaches are computationally cheap and provide a guaranteed valid floor.

**Member ideas:**
- idea_001: Basic X.-X cancellation (ESTABLISHED — works universally)
- idea_002: X.Y.-X heuristic (DEBUNKED — invalid for Megaminx)
- idea_005: Commutator/identity discovery (ACTIVE — unexplored)

**Best achieved:** 46312 (compression_ratio=0.9158) via basic cancellation.

**Status:** Baseline is established. Higher scores require moving beyond compression into actual search.