# State of Affairs — Gen 004

## Current Standing

**Best score: 44094** (gen003_explore_2_sol01 — compression + raw-integer predictor tail search).
Gen004 regressed to 44111 (exploit_1_sol01 — full combined recipe with embedding MLP + MITM). 4 generations run. **Trajectory: plateaued.** Compression exhausted at 44114; predictor tested twice with marginal results (20 and 3 moves saved respectively). Gap to target: 29094 proxy moves.

## What Works

- **Empirical algebraic identity compression (idea_009, established, conf 0.95):** 8 solutions converge at 44114 (compression_ratio=0.8723). This is the guaranteed floor. Always apply first.
- **X.-X cancellation (idea_001, established, conf 0.95):** Universal baseline at 46312.
- **CayleyPy beam search API (idea_012, conf 0.9):** `bfs_result_for_mitm` MITM backstop verified working. Must use same CayleyGraph instance for BFS and beam search (hasher seed compatibility).
- **MlpModel one-hot architecture (idea_014, conf 0.65):** CayleyPy's built-in model uses `nn.functional.one_hot()`, NOT raw integers. Proven on Rubik's 98% optimality. Agents should use `MlpModel(graph, hidden_dims=[512,256])` instead of custom architectures.

## Current Frontier

**The binding constraint is training data depth, not model architecture.** Two generations of architecture fixes (embedding → one-hot) produced no meaningful improvement because the predictor never sees states at depth 100+, where 74.8% of the score lives.

**Priority 1 — path-intermediate training data (idea_016):** Extract (state, remaining_depth) pairs from compressed solution paths. Covers depths 1–888 across all buckets. Approximate labels (compressed ≠ optimal) but correlated with true distance. **Warning:** gen003 explore_2 tried this with raw integer MLP and got loss ~6000 (useless). Must be re-tested with correct architecture (MlpModel or embedding).

**Priority 2 — large beam width (pattern_009):** CayleyPy paper shows log-linear quality scaling with beam_width. All experiments used beam_width ≤ 4096. Target: 65536 with `graph.batch_size=2048` (~300 MB/batch). This may be the single largest lever.

**Priority 3 — non-backtracking beam search (idea_015, conf 0.6):** Advanced mode (`beam_mode='advanced'`) quadruples success rate per CayleyPy paper. **Mutually exclusive with MITM** (idea_012). Need head-to-head comparison to pick.

## Coverage Map

| Approach | Solutions | Best | Status |
|----------|-----------|------|--------|
| Compression only | 17+ | 44114 | EXHAUSTED |
| Compression + raw-integer predictor (tail search) | 1 | 44094 | ALL-TIME BEST |
| Compression + embedding predictor + MITM (full-path) | 1 | 44111 | Marginal |
| BFS-only training predictor | 1 test | — | USELESS for deep states |
| Path-intermediate training + MlpModel + beam_width≥65536 | 0 | — | UNTESTED — top priority |
| Non-backtracking beam (advanced mode) | 0 | — | UNTESTED |
| GNN predictor | 0 | — | UNTESTED |

**Entirely unexplored:** Deep training data, large beam widths, non-backtracking mode, per-bucket strategies, curriculum learning, ensemble predictors.

## Dead Ends

1. **Compression-only approaches:** Ceiling at 44114 confirmed by 8 solutions. No further work.
2. **Shallow training data predictors:** Both BFS (depth 0-6) and random walks (depth 0-50) produce predictors useless for hard/very_hard puzzles (99% of score). Pattern_008 confirmed.
3. **Unguided beam search:** Adds nothing at any beam width. 10+ solutions confirm.
4. **Hamming predictor (idea_006):** Zero advantage over unguided. Debunked.
5. **Corner-only PDB (idea_007):** All generators are 5-cycles. Debunked.
6. **Experimentator role for helper writing:** 3 consecutive generations of zero output. Stop assigning.

## Open Questions

1. **Does path-intermediate training with correct architecture beat 44114?** gen003 failed with raw integer MLP (loss ~6000). With MlpModel/embedding, loss should drop dramatically, but approximate labels add noise. This is THE experiment for gen005.
2. **Non-backtracking vs MITM — which is better for very_hard puzzles?** Mutually exclusive. Non-backtracking prunes ~1/24 of search per step; MITM saves 6 fixed steps. For depth 500-1000 puzzles, non-backtracking likely dominates.
3. **Was gen003's 44094 due to tail-search strategy, not the predictor?** gen003 used sliding-window suffix search; gen004 used full-path search. Different strategies, different results. The 44094 may not be reproducible with full-path search even with better training data.
4. **What beam_width does our RTX 5060 Ti support before OOM?** research_1 estimated 65536 with batch_size=2048. Unverified. Need empirical profiling.
5. **Do Kaggle top solutions (~8050 proxy) use beam search at all?** The CayleyPy team created the competition and publishes the beam search approach. Gap is 5.6x. We may need diffusion-distance training or DQN refinement (described in CayleyPy RL paper) rather than simple supervised learning.

**very_hard bucket (ids 501-1000) = 74.8% of score.** Every experiment must prioritize this bucket.
