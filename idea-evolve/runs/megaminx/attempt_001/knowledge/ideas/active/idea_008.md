---
type: idea
id: idea_008
name: Trained MLP predictor-guided beam search
lifecycle: active
confidence: 0.7
first_seen: gen_002
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: [gen002_research_1]
contradicted_by: []
related_ideas: [idea_003, idea_006]
cluster: machine_learning
tags: [predictor, MLP, beam_search, ML, trained_predictor]
---

# Trained MLP Predictor-Guided Beam Search

## Summary

Train a neural network (MLP) on random-walk distance data to predict actual optimal
distance from any Megaminx state. Use this predictor to guide beam search toward
shorter paths than compression can achieve. research_1 confirmed the complete pipeline:
`graph.random_walks()` → PyTorch MLP training → `Predictor(graph, model)` →
`graph.beam_search(predictor=predictor)`.

## Evidence from Gen 2

**research_1 (findings.md):** Confirmed that:
- `graph.random_walks(width=50000, length=20, mode='bfs')` generates 50k (state, distance)
  training pairs from the solved state
- `Predictor(graph, model)` accepts a trained PyTorch model
- Beam mode must be `'simple'` to get actual paths (advanced mode has a path-return bug)
- The pipeline was proven functional but no solution actually ran end-to-end with a trained predictor

**CRITICAL FINDING from research_1:** The hamming predictor provides ZERO advantage over
unguided search. This definitively answers EXP-1: hamming is not the path forward.
Only a trained MLP predictor can potentially beat compression.

## Pipeline

```python
import torch
gdef = cayleypy.Puzzles.megaminx()
graph = cayleypy.CayleyGraph(gdef, dtype=torch.int8)  # GPU, int8

# Generate training data: random walks from solved state
X, y = graph.random_walks(50000, 20, mode='bfs')  # 50k samples, length 20 walks

# Train MLP
model = torch.nn.Sequential(
    torch.nn.Linear(120, 256), torch.nn.ReLU(),
    torch.nn.Linear(256, 128), torch.nn.ReLU(),
    torch.nn.Linear(128, 1)
)
# Train with MSE on distance

# Use in beam search
predictor = cayleypy.Predictor(graph, model)
res = graph.beam_search(start_state=state, beam_width=8192, max_steps=80,
                        predictor=predictor, beam_mode='simple',
                        return_path=True, verbose=0)
```

## Key Unknown

Whether the trained predictor's accuracy on depth-20 random walks generalizes to
depth-100+ puzzles in the hard/very_hard buckets. This is the central research question
for gen 3.

## Status

ACTIVE — highest priority experiment for gen 3. The pipeline is confirmed functional.
The question is whether the predictor can guide beam search to paths shorter than
compression achieves (~44114 with empirical identities).

## Beam Width Requirements

research_1 found beam_width must be 4x-32x larger than gen001 used:
- depth 10: beam_width=32768 solves optimally
- depth 26-100: beam_width=65536 needed but too slow
- depth 500-1000 (very_hard): astronomical beam width required without perfect predictor

The trained predictor must compensate for beam width limitations by better guiding the search.

**NOTE:** Never actually tested end-to-end after 2 generations. This is the primary path to the target and it has never been executed.