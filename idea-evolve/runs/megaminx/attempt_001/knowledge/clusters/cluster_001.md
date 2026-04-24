---
type: cluster
id: cluster_001
name: Compression baseline
member_ideas: [idea_001, idea_005, idea_009]
best_score: 44114
best_solution: gen002_explore_2_sol01
status: exhausted_as_standalone
last_updated: gen_004
---

# Cluster: Compression Baseline

Compression approaches operate on the sample_submission paths directly, removing
redundant move sequences without search. These approaches are computationally cheap
and provide a guaranteed valid floor.

**Member ideas:**
- idea_001: Basic X.-X cancellation (ESTABLISHED — works universally)
- idea_005: Commutator/identity discovery (ESTABLISHED — 6 solutions confirmed)
- idea_009: Empirical algebraic identity compression (ESTABLISHED — 7+ solutions, ceiling at 44114)

**Best achieved (compression alone):** 44114 (gen002_explore_2_sol01)

**Status:** EXHAUSTED as standalone. The compression ceiling at 44114 has been confirmed
across 7 solutions over 3 generations. No further compression-only improvements are possible.

Its role is exclusively as Phase 1 baseline for hybrid approaches (search + predictor).
The 336-rule set (from idea_009) is stable and should be included in every solution
as a fallback guarantee.

**Gen004 note:** The combined predictor pipeline (idea_013) scored 44111 — only 3 moves
better than compression alone, and worse than gen003's 44094. Compression is effectively
the performance ceiling until deep training data (idea_016) is implemented.
