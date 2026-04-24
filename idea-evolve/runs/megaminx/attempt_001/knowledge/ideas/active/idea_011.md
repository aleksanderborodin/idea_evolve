---
type: idea
id: idea_011
name: Embedding-based MLP predictor for permutation states
lifecycle: active
confidence: 0.55
first_seen: gen_003
last_updated: gen_004
last_confirmed_gen: gen_004
supported_by: [gen003_research_1]
contradicted_by: [gen004_exploit_1_sol01]
related_ideas: [idea_008, idea_010, idea_014]
cluster: search_algorithms
tags: [embedding, predictor, MLP, categorical, architecture, memory_efficient]
---

# Embedding-Based MLP Predictor for Permutation States

## Summary

Replace the raw-integer MLP (which treats permutation positions as ordinal values) with
an embedding-based architecture that correctly handles the categorical nature of permutation
states. Achieves 5.3x lower training loss on shallow data. **However, gen004 testing showed
this lower training loss does NOT translate to better beam search results** — the embedding
MLP (44111) performed worse than the raw integer MLP (44094). Training data depth, not
architecture, is the binding constraint.

## Confidence Note

Confidence reduced from 0.85 to 0.55 by consistency reviewer gen004. While the embedding
architecture achieves lower training loss (0.86 vs 4.57), this has NOT translated to better
beam search effectiveness. gen004_exploit_1_sol01 used the embedding MLP and scored 44111
(WORSE than gen003's raw-integer 44094). The lower training loss on shallow data does not
predict better guidance for deep puzzles.

## The Problem with Raw Integer MLP

The existing `_PredictorMLP` in `helpers/trained_predictor_beam_search.py` casts int64 state
tensors to float32 and passes them through linear layers. This treats each of the 120
position values as ordinal integers where value 119 is "close to" 118 and "far from" 0.
But the state is a **permutation** — position 3 holding value 47 is categorically different
from position 3 holding value 48.

## Relationship to idea_014 (MlpModel one-hot)

**CayleyPy's built-in MlpModel uses one-hot encoding (`nn.functional.one_hot()`), NOT raw
integers.** Our earlier assumption that CayleyPy uses raw integers was wrong. The library's
proven approach is one-hot, not embedding. For agents using CayleyPy's Predictor interface,
MlpModel (idea_014) is the recommended approach — it's the library's own model with proven
results on Rubik's cubes.

The embedding approach (this idea) remains valid as a **memory-efficient alternative** when
one-hot encoding causes OOM at large beam widths. At beam_width=65536, one-hot uses ~300 MB
per batch (manageable) but embedding (dim=32) uses only ~80 MB.

## The Embedding Architecture

```python
class EmbeddingMLP(nn.Module):
    def __init__(self, state_size=120, num_classes=120, embed_dim=32):
        super().__init__()
        self.embed = nn.Embedding(num_classes, embed_dim)
        input_dim = state_size * embed_dim  # 120 * 32 = 3840
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512), nn.LayerNorm(512), nn.ReLU(),
            nn.Linear(512, 256), nn.LayerNorm(256), nn.ReLU(),
            nn.Linear(256, 1)
        )
    def forward(self, x):
        x = self.embed(x.long()).flatten(start_dim=-2)
        return self.net(x).squeeze(-1)
```

## Evidence

| Architecture | Training Loss (20 epochs, 226k samples) | Beam Search Result |
|---|---|---|
| Raw integer MLP (existing helper) | 4.57 | 44094 (gen003, tail search) |
| Embedding MLP (120x32 embed) | 0.86 | 44111 (gen004, full-path search) |

Lower training loss does NOT guarantee better beam search effectiveness. The dominant
factor is training data depth (see pattern_008, idea_016).

## Memory Efficiency

During beam search inference at beam_width=65536 with batch_size=2048:

| Architecture | Memory per batch |
|---|---|
| One-hot (MlpModel, 14,400 features) | ~300 MB |
| Embedding (dim=32, 3,840 features) | ~80 MB |
| Embedding (dim=16, 1,920 features) | ~40 MB |

Embedding is the fallback if MlpModel causes OOM at very large beam widths.
