---
type: idea
id: idea_003
name: Predictor-guided beam search
lifecycle: active
confidence: 0.7
first_seen: gen_001
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: [gen001_research_1, gen002_research_1]
contradicted_by: []
related_ideas: [idea_006, idea_008]
cluster: machine_learning
tags: [beam_search, predictor, ML, guided_search]
---

# Predictor-Guided Beam Search

## Summary

Train a model to predict distance-to-solved for any Megaminx state. Use this predictor
as a heuristic in beam search to guide exploration toward promising states. This is
the approach used by top Kaggle entrants (~8050 proxy). The complete pipeline is
confirmed functional by research_1 (gen001 and gen002).

## Evidence

**Pipeline CONFIRMED WORKING (research_1 gen002):**
- `Puzzles.megaminx()` returns CayleyGraphDef
- `graph.random_walks(width, length, mode='bfs')` produces training pairs (50k samples, 20 steps)
- `Predictor(graph, model)` accepts a trained PyTorch model
- Training loop: MSE 3.46 → 0.86 in 3 epochs on 1000 samples (confirming learning works)
- `beam_search(predictor=...)` accepts a predictor
- `beam_mode='simple'` required for path return (advanced mode has a bug returning path=None)

**NEVER ACTUALLY TESTED with trained predictor:** No solution has run end-to-end with a
trained MLP predictor. research_1 confirmed the pipeline works but didn't execute the full
experiment. No solution has beaten compression using predictor-guided beam search.

**CONFLICT with idea_006:** Hamming predictor provides ZERO advantage (DEBUNKED below).
Only a trained MLP predictor can potentially guide beam search to beat compression.

## Pipeline (from research_1)

```python
import torch
gdef = cayleypy.Puzzles.megaminx()
graph = cayleypy.CayleyGraph(gdef, dtype=torch.int8)
X, y = graph.random_walks(50000, 20, mode='bfs')
model = torch.nn.Sequential(torch.nn.Linear(120, 256), torch.nn.ReLU(),
                           torch.nn.Linear(256, 128), torch.nn.ReLU(),
                           torch.nn.Linear(128, 1))
# Train with MSE loss
predictor = cayleypy.Predictor(graph, model)
res = graph.beam_search(start_state=state, beam_width=8192, max_steps=80,
                        predictor=predictor, beam_mode='simple', return_path=True)
```

## Critical Unknown

Whether the trained predictor's accuracy on depth-20 random walks generalizes to
depth-100+ puzzles. This is the central research question for gen 3.

## Why It Matters

If a predictor can guide beam search to find paths that compression misses (especially
on very_hard bucket), the target of 15000 becomes realistic. The very_hard bucket
contributes 75% of the score.

## Status

ACTIVE — highest priority next experiment. Pipeline confirmed functional.
The question is whether the predictor can guide beam search to paths shorter than
compression achieves (~44114 with empirical identities).
