---
type: cluster
id: cluster_002
name: Search algorithms
member_ideas: [idea_003, idea_004, idea_008, idea_010, idea_011, idea_012, idea_013, idea_014, idea_015, idea_016]
best_score: 44094
best_solution: gen003_explore_2_sol01
status: active
last_updated: gen_004
---

# Cluster: Search Algorithms

Search-based approaches explore the Megaminx state space to find shorter paths
than compression. This cluster includes beam search, MITM, predictor training,
and their combinations.

**Member ideas:**
- idea_003: Predictor-guided beam search (ACTIVE — pipeline confirmed)
- idea_004: Meet-in-the-middle BFS (ACTIVE — superseded by idea_012)
- idea_008: Trained MLP predictor-guided beam search (ACTIVE — tested 2 gens, marginal results; bottleneck is training data depth)
- idea_010: BFS-derived exact-distance training data (ACTIVE — useful for MITM, NOT as sole training source for deep predictor)
- idea_011: Embedding-based MLP predictor (ACTIVE — better loss than raw integer, still marginal results)
- idea_012: Built-in MITM+beam via bfs_result_for_mitm (ACTIVE — verified working)
- idea_013: Combined recipe BFS+embedding+MITM (ACTIVE — TESTED gen004: 44111, worse than gen003; needs deep training data)
- idea_014: CayleyPy built-in MlpModel with one-hot encoding (ACTIVE — proven library architecture, untested in solution)
- idea_015: Non-backtracking beam search (ACTIVE — quadruples success rate, mutually exclusive with MITM, untested in solution)
- idea_016: Path-intermediate states as deep training data (ACTIVE — top priority, never tested, addresses the core bottleneck)

**Current status (gen004 update):**
- Compression alone: exhausted at 44114 (7 solutions confirm)
- Predictor pipeline (raw integer MLP): marginal at 44094 (gen003)
- Predictor pipeline (embedding MLP + random walks depth 50 + MITM + beam_width=4096): 44111 (gen004 — REGRESSION)
- Path-intermediate training (idea_016): UNTESTED — top priority
- Large beam width (65536+): UNTESTED — second priority
- MlpModel one-hot (idea_014): UNTESTED in solution
- Non-backtracking beam (idea_015): UNTESTED in solution

**Critical bottleneck identified:** Training data depth. Predictors trained on depth ≤50 
have zero guidance power for very_hard puzzles (depth 501–1000, 74.8% of score). This
is confirmed empirically (gen004 exploit_1 BFS-only = constant prediction of ~4; random
walk depth 50 = marginal improvement on 2/101 puzzles).

**Next experiments (priority order):**
1. Path-intermediate training + MlpModel + large beam_width (65536) (idea_016 + idea_014)
2. Non-backtracking (idea_015) vs MITM (idea_012) head-to-head at same beam width
3. Long random walks (depth 200–500) as alternative deep training data

**Best achieved:** 44094 (gen003_explore_2_sol01 — compression + raw integer predictor tail search)
