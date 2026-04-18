---
type: cluster
id: cluster_001
name: Compression baseline
member_ideas: [idea_001, idea_005, idea_009]
best_score: 44114
best_solution: gen002_explore_2_sol01
status: active
last_updated: gen_002
---

# Cluster: Compression Baseline

Compression approaches operate on the sample_submission paths directly, removing
redundant move sequences without search. These approaches are computationally cheap
and provide a guaranteed valid floor.

**Member ideas:**
- idea_001: Basic X.-X cancellation (ESTABLISHED — works universally)
- idea_005: Commutator/identity discovery (ESTABLISHED — 6 solutions confirmed)
- idea_009: Empirical algebraic identity compression (ACTIVE — best at 44114)

**Best achieved:** 44114 (compression_ratio=0.8723) via empirical identity rules.

**Status:** Baseline is established. Higher scores require search-based methods.
The compression ceiling (~44114) is confirmed — compression alone cannot reach
the 15000 target.

## gen_002 Advance

gen_002 found a new compression floor at 44114 (44114 < 46312). This is a genuine
improvement from algebraic identity compression (idea_009). The key insight:
empirical discovery of commutators/conjugations from sample_submission outperforms
systematic enumeration.
