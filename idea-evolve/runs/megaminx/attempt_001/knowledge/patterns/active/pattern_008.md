---
type: pattern
id: pattern_008
name: Predictor trained on shallow data cannot guide deep beam search
lifecycle: active
confidence: 0.9
first_seen: gen_004
last_updated: gen_004
evidence: [gen004_exploit_1_sol01]
related_ideas: [idea_010, idea_011, idea_016]
tags: [predictor, training_depth, generalization, beam_search, failure_mode]
---

# Predictor Trained on Shallow Data Cannot Guide Deep Beam Search

## Observation

exploit_1 (gen004) tested the combined recipe (idea_013) with two training data sources:
BFS depth-6 data (exact labels, depths 0-5) and random walks (noisy labels, depths 0-49).
Neither produced a predictor that could effectively guide beam search on the hard/very_hard
puzzles that dominate the score.

**BFS-only predictor:** Predicts every state as depth ~4 regardless of actual depth. Completely
useless for puzzles deeper than ~10. The predictor has zero information about the distribution
of states at depth 100+.

**Random walk predictor (depth 50):** Trains to loss 2.83 on its training distribution but
fails to generalize. Beam search with this predictor improved only 2 out of 101 puzzles
(saving 3 moves total against the 44114 compression baseline).

## Key Insight

The predictor's training distribution depth is the critical bottleneck — NOT model architecture
(the embedding MLP from idea_011 trained well and achieved low loss on its training data).
A perfect model with shallow training data is useless for deep puzzles. The 74.8% of score
in the very_hard bucket (depth 500-1000) requires a predictor that can distinguish states
at those depths.

## Implication

Future training data MUST cover the full depth range (0-888). Options:
1. Path-intermediate states from compressed paths (idea_016, covers full range)
2. Longer random walks (depth 200-500) — exploit_1's #1 suggestion
3. Curriculum learning — train on shallow data first, then fine-tune on deeper data
