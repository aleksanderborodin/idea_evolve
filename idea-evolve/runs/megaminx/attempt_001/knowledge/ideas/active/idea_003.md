---
type: idea
id: idea_003
name: Predictor-guided beam search
lifecycle: active
confidence: 0.6
first_seen: gen_001
last_updated: gen_003
last_confirmed_gen: gen_003
supported_by: [gen001_research_1, gen002_research_1, gen003_explore_2_sol01]
contradicted_by: []
related_ideas: [idea_006, idea_008, idea_010, idea_011, idea_012]
cluster: search_algorithms
tags: [beam_search, predictor, ML, guided_search]
---

# Predictor-Guided Beam Search

## Summary

Train a model to predict distance-to-solved for any Megaminx state. Use this predictor
as a heuristic in beam search to guide exploration toward promising states. This is
the approach used by top Kaggle entrants (~8050 proxy). The complete pipeline is
confirmed functional by research_1 (gen001 and gen002). gen003 tested it end-to-end
with a raw integer MLP predictor — marginal improvement (44094, 20 moves over compression).

## Evidence

**Pipeline CONFIRMED WORKING (research_1 gen002):**
- `Puzzles.megaminx()` returns CayleyGraphDef
- `graph.random_walks(width, length, mode='bfs')` produces training pairs
- `Predictor(graph, model)` accepts a trained PyTorch model
- `beam_search(predictor=...)` accepts a predictor
- `beam_mode='simple'` required for path return (advanced mode returns path=None)

**TESTED END-TO-END (gen003 explore_2_sol01):**
- Raw integer MLP predictor trained on random walks (50k, depth 20)
- Sliding-window beam search on path suffixes (tail optimization)
- Result: 44094 (only 20 moves better than compression alone)
- Predictor effective range: suffixes ≤12 moves from solved state

**The model architecture matters critically.** The raw integer MLP (existing helper) treats
permutation positions as ordinal values, yielding training loss 4.57. An embedding-based
model achieves loss 0.86 (5.3x better, see idea_011). The marginal gen003 result is
explained by the wrong architecture, not a failure of the concept.

## Updated Pipeline (incorporating gen003 findings)

```python
import torch
gdef = cayleypy.Puzzles.megaminx()
graph = cayleypy.CayleyGraph(gdef, dtype=torch.int8)
# Use BFS data instead of random walks (idea_010)
bfs_result = graph.bfs(max_diameter=6, return_all_hashes=True,
                       max_layer_size_to_explore=10**9)
# Extract training data from BFS layers
X, y = extract_bfs_training_data(bfs_result)
# Use embedding model instead of raw integer MLP (idea_011)
model = EmbeddingMLP(state_size=120, num_classes=120, embed_dim=32)
# Train and use predictor
predictor = cayleypy.Predictor(graph, model)
res = graph.beam_search(start_state=state, beam_width=4096, max_steps=200,
                        predictor=predictor, beam_mode='simple', return_path=True,
                        bfs_result_for_mitm=bfs_result)
```

## Critical Unknowns

1. **Does the corrected architecture (embedding MLP + BFS data + MITM) substantially beat 44114?**
   The raw integer predictor was ineffective. The corrected pipeline is the gen004 priority.
2. **What training depth generalizes to depth-500+ puzzles?** BFS data only covers depth 0-6.
   The predictor must generalize far beyond its training distribution for very_hard puzzles.
3. **What beam width is needed per bucket with MITM backstop?** MITM reduces required depth by 6,
   but depth-500 puzzles still need beam search to reach depth ~494.

## Status

ACTIVE. Pipeline confirmed functional AND tested end-to-end (with suboptimal architecture).
The corrected architecture (idea_011) with better training data (idea_010) and MITM backstop
(idea_012) is the highest priority experiment for gen004.
