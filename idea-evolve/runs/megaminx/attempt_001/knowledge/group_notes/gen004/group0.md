# Group 0 notes — generation 4

## Agents in this group
- exploit_1 — 1 solution, best score 44111
- experimentator_1 — 0 solutions (timed out, zero output, 2nd consecutive failure)
- research_1 — 0 solutions (research role, produced major findings from paper/code analysis)

## What they tried
- exploit_1: Full combined recipe (idea_013) — compression (336 rules → 44114) + BFS depth 6 MITM + embedding MLP predictor trained on random walks (depth 50, 2.3M samples) + guided beam search (beam_width=4096). Final: 44111 (3 moves saved vs compression alone).
- experimentator_1: Supposed to build `embedding_predictor_beam.py` helper. Timed out with zero output. This is the 2nd consecutive gen the experimentator has failed on this task.
- research_1: Read CayleyPy RL paper (arXiv:2502.18663), CayleyPy-1 paper, CayleyPy source code (`models/models.py`, `predictor.py`, `cayley_graph.py`, `algo/beam_search.py`), DeepCubeA paper. No Kaggle write-ups exist.

## What worked
- exploit_1's embedding MLP trains well (loss 2.83 in 44s on 2.3M samples) — architecture is sound
- exploit_1 confirmed the combined recipe pipeline is mechanically functional end-to-end
- research_1's source code analysis revealed the correct architecture and critical scaling insight

## What didn't work
- BFS-only training data (depth 0-5) produces a completely useless predictor — predicts every state as ~4
- Random walk data (depth ≤49) only marginally better — beam search improved 2/101 puzzles, saving 3 moves
- experimentator failed again (0 output) — helper module remains unbuilt for 3 generations
- beam_width=4096 is far too small; the CayleyPy paper shows log-linear scaling with beam width

## Critical findings from research_1 (ACT ON THESE)

1. **CayleyPy's MlpModel uses one-hot encoding** (NOT raw integers). Located at `models/models.py`. Use it directly instead of building custom models. See new idea_014.
2. **Non-backtracking beam search quadruples success rate** (17.6% → 69.7%) per the CayleyPy-1 paper. Use `beam_mode='advanced'` WITH a predictor. INCOMPATIBLE with MITM (`bfs_result_for_mitm`). See new idea_015.
3. **Beam width is THE dominant parameter.** Solution quality scales linearly with log(beam_width). We've been using 4096; should target 65536+. See new pattern_009.
4. **The real bottleneck is training data depth**, not model architecture. exploit_1 confirmed the embedding MLP trains well but cannot guide deep beam search when trained on depth ≤50 data. exploit_1 suggested path-intermediate training data as the fix (see new idea_016).

## Open questions for next groups
- Can we use non-backtracking mode (idea_015) AND MITM simultaneously, or must we choose?
- What beam_width can we achieve before OOM with one-hot MlpModel on RTX 5060 Ti (16 GB)?
- Does path-intermediate training data (idea_016) actually help the predictor generalize to deep states?
- Should we abandon the experimentator role for helper creation and have a full/explore agent embed the code inline?

## New ideas registered (filenames only)
- idea_014 — Use CayleyPy built-in MlpModel with one-hot encoding
- idea_015 — Non-backtracking beam search (advanced beam mode)
- idea_016 — Path-intermediate states as deep training data
- pattern_008 — Predictor trained on shallow data cannot guide deep beam search
- pattern_009 — Solution quality scales logarithmically with beam width
