---
type: pattern
id: pattern_006
name: Raw integer MLP predictor is ineffective — categorical representation required
lifecycle: active
confidence: 0.9
first_seen: gen_003
last_updated: gen_003
evidence: [gen003_research_1, gen003_explore_2_sol01]
related_ideas: [idea_008, idea_011]
tags: [predictor, architecture, categorical, embedding, representation]
---

# Raw Integer MLP Predictor Is Ineffective — Categorical Representation Required

## Observation

The existing helper's `_PredictorMLP` treats the 120-element Megaminx state as a vector
of ordinal integers, casting int64 to float32 and passing through linear layers. This is
fundamentally wrong because the state is a **permutation** — the values represent categories,
not ordered quantities. Value 47 at position 3 is not "close to" value 48.

**Controlled experiment (research_1 gen003):**
- Raw integer MLP: training loss 4.57
- Embedding-based MLP: training loss 0.86 (5.3x better)

**Real-world evidence (explore_2 gen003):**
- sol01 with raw integer MLP: 44094 (only 20 moves better than compression)
- The predictor could only solve suffixes ≤12 moves from solved

## Implication

Two generations of failed predictor experiments (gen002 exploit_1 state-encoding error,
gen003 explore_2 marginal improvement) are explained by the wrong model architecture.
The fix is straightforward: replace raw integer input with categorical embeddings
(`nn.Embedding(120, 32)` per position). Every future predictor must use embedding-based
or one-hot input representation.

## Broader Lesson

When the input is a permutation or categorical data (common in combinatorial puzzles),
never treat it as ordinal integers regardless of the model type. Always use embeddings
or one-hot encoding. This applies to any future ML-based approach (GNNs, transformers, etc.).
