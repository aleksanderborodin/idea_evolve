---
type: idea
id: idea_010
name: BFS-derived exact-distance training data for predictor
lifecycle: active
confidence: 0.35
first_seen: gen_003
last_updated: gen_004
last_confirmed_gen: gen_004
supported_by: [gen003_research_1]
contradicted_by: [gen004_exploit_1_sol01]
related_ideas: [idea_008, idea_003, idea_012, idea_016]
cluster: search_algorithms
tags: [BFS, training_data, exact_distances, predictor, GPU, MITM]
---

# BFS-Derived Exact-Distance Training Data for Predictor

## Summary

BFS from the solved state to depth 6 produces exact-distance training samples covering
states at distances 0–6. **CRITICAL: Using BFS data as the *sole* training source for a
predictor produces a USELESS predictor for deep puzzles** — it predicts every state as
depth ~4, regardless of actual depth (confirmed gen004 exploit_1). The earlier claim that
BFS data is "strictly superior to random walks" is **WRONG** for the predictor use case.

BFS data remains valuable for:
1. **MITM backstop** — pass `bfs_result_for_mitm` to beam search to halve required beam depth (idea_012). This is its primary value.
2. **Supplementary training** — combine with deep training data (idea_016: path intermediates) to provide accurate labels for shallow states.

## Confidence Note

Confidence reduced from 0.6 to 0.35 by consistency reviewer gen004. The primary claim
("strictly superior training data") was refuted empirically. The idea retains value for
MITM and supplementary shallow-state training, but its role is now clearly secondary to
deep training data (idea_016).

## Evidence

research_1 (gen003) measured BFS layer sizes:

| Depth | States | Cumulative | Growth Factor |
|-------|--------|------------|---------------|
| 0     | 1      | 1          | -             |
| 1     | 24     | 25         | 24x           |
| 2     | 408    | 433        | 17x           |
| 3     | 6,208  | 6,641      | 15.2x         |
| 4     | 90,144 | 96,785     | 14.5x         |
| 5     | 1,280,160 | 1,376,945 | 14.2x      |
| 6     | 17,975,460 | 19,352,405 | 14.0x     |

Every label is EXACT (BFS guarantees shortest path). Computed in ~1s on GPU.
**Important:** On a 16 GB GPU, only layers 0–5 (~1.38M states) can be decoded to full state
tensors; layer 6 (~17.9M states) OOMs.

**Gen004 empirical result (exploit_1):** A predictor trained on BFS layers 0–5 alone
predicts every deep state as depth ~4 (the average training depth). Completely useless
for hard puzzles (depth 101–300) and very_hard puzzles (depth 501–1000).

## Revised Role

BFS data is **necessary but not sufficient** for training a useful predictor:
- **Use for MITM** (free): same computation, major beam search benefit.
- **DO NOT use as sole training source** for a predictor intended to guide deep beam search.
- **Supplement with depth 100+ data**: path-intermediate states from compressed paths
  (idea_016 — the highest priority).

## Implementation Note

```python
# BFS for MITM backstop (always useful):
bfs_result = graph.bfs(max_diameter=6, return_all_hashes=True,
                       max_layer_size_to_explore=10**9)
# Pass to beam search:
graph.beam_search(start_state=state, bfs_result_for_mitm=bfs_result, ...)

# BFS training data (layers 0-5 only — avoid OOM on layer 6):
X_list, y_list = [], []
for depth in range(6):
    layer = bfs_result.layers[depth]
    X_list.append(layer)
    y_list.append(torch.full((len(layer),), depth))
# Combine with deep training data before training predictor.
```
