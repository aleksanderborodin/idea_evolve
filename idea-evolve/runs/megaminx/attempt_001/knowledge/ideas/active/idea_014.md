---
type: idea
id: idea_014
name: Use CayleyPy built-in MlpModel with one-hot encoding
lifecycle: active
confidence: 0.65
first_seen: gen_004
last_updated: gen_004
last_confirmed_gen: gen_004
supported_by: [gen004_research_1]
contradicted_by: []
related_ideas: [idea_011, idea_008, idea_003]
cluster: search_algorithms
tags: [cayleypy, one_hot, MlpModel, library_model, proven_architecture]
---

# Use CayleyPy Built-In MlpModel with One-Hot Encoding

## Summary

CayleyPy's official `MlpModel` class (in `models/models.py`) uses `nn.functional.one_hot()`
to encode the 120-element permutation state into a 14,400-dim sparse vector, followed by
multi-layer perceptron layers. This is the proven, tested architecture that the CayleyPy team
uses to achieve 98% optimality on 3x3 Rubik's cubes.

## Confidence Note

Confidence reduced from 0.85 to 0.65 by consistency reviewer gen004. The architecture is
proven on Rubik's cubes and well-documented in the CayleyPy source, but it has NEVER been
tested on a Megaminx solution. The 98% optimality claim is for a different puzzle. Megaminx
may have different characteristics. Still the strongest candidate model architecture.

## Why This Matters

Research_1 (gen004) read the CayleyPy source code and discovered that `MlpModel` uses one-hot
encoding — NOT raw integers as we assumed for 2 generations. Our idea_011 proposed a custom
embedding MLP as the fix for the raw-integer problem. While the embedding approach is
architecturally valid, using the library's proven model avoids reinventing the wheel and
guarantees compatibility with the `Predictor` class.

## Implementation

```python
from cayleypy.models import MlpModel
gdef = cayleypy.Puzzles.megaminx()
graph = cayleypy.CayleyGraph(gdef, dtype=torch.int8)
model = MlpModel(graph, hidden_dims=[512, 256])
predictor = cayleypy.Predictor(graph, model)
```

## Memory Consideration

One-hot encoding produces a 14,400-dim input (120 positions x 120 classes). At beam_width=8192
that's ~10.9 GB per batch. For large beam widths (65536+), use `graph.batch_size=2048` or
reduce to embedding (idea_011) if OOM occurs. At beam_width=65536 with batch_size=2048,
the peak memory per batch is manageable (~300 MB).
