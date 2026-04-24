---
type: idea
id: idea_008
name: Trained MLP predictor-guided beam search
lifecycle: active
confidence: 0.4
first_seen: gen_002
last_updated: gen_004
last_confirmed_gen: gen_004
supported_by: [gen002_research_1, gen003_explore_2_sol01, gen004_exploit_1_sol01]
contradicted_by: []
related_ideas: [idea_003, idea_006, idea_010, idea_011, idea_012, idea_014, idea_015, idea_016]
cluster: search_algorithms
tags: [predictor, MLP, beam_search, ML, trained_predictor]
---

# Trained MLP Predictor-Guided Beam Search

## Summary

Train a neural network on distance data to predict optimal distance from any Megaminx
state. Use this predictor to guide beam search toward shorter paths than compression
can achieve. Two generations of end-to-end testing confirm the pipeline works but
the improvement is marginal regardless of model architecture. **The bottleneck is
training data depth, not model architecture.**

## Evidence from Gen 3 and Gen 4

**gen003 (explore_2_sol01, raw integer MLP):** 44094 — 20 moves over compression. Marginal
improvement explained by wrong architecture (raw integers for categorical data).

**gen004 (exploit_1_sol01, embedding MLP):** 44111 — 3 moves over compression. WORSE than
gen003 despite using the correct architecture (embedding-based categorical representation).
Training data: random walks depth 50. Improved 2/101 puzzles.

**CRITICAL FINDING:** The architecture fix (embedding vs raw integers) did not help. Both
experiments confirm the predictor fails to guide beam search on hard/very_hard puzzles.
The root cause is now clearly identified as **training data depth**: the predictor has
no information about states at depth 100+, regardless of how well it represents shallow
states.

## Updated Diagnosis

```
Gen003 hypothesis: "Architecture is wrong (raw integers)"
Gen004 result: "Architecture was fixed — still marginal"
New hypothesis: "Training data doesn't cover the depth range that matters"
```

The 74.8% of score comes from very_hard puzzles (depth 501–1000). Predictor trained on
depth ≤50 data (BFS or random walks) has zero predictive power there.

## Path Forward

1. **Training data:** Use path-intermediate states (idea_016) — these cover depths 1–888
   with approximate but correlated distance labels. This is now the #1 priority.
2. **Model:** Use CayleyPy's built-in MlpModel (idea_014) — proven architecture, no
   custom implementation needed.
3. **Beam width:** Scale to 65536+ (pattern_009 — log-linear improvement).
4. **Beam mode:** Test non-backtracking (idea_015) vs MITM (idea_012) — mutually exclusive,
   need to pick the better option.

## Architecture Reference

Embedding MLP (idea_011) achieves 5.3x lower loss than raw integer MLP. MlpModel (idea_014,
one-hot) is the library's proven approach. Either architecture is acceptable for the model
itself — training data depth is the binding constraint.
