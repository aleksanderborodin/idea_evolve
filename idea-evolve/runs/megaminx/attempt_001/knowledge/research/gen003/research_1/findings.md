# Research Findings — Gen003: CayleyPy Internals, Model Architecture, and MITM+Beam

## Summary

I performed deep source-code analysis of the cayleypy library (predictor.py, beam_search.py, random_walks.py, models.py, cayley_graph.py) and ran targeted experiments. The central findings are: **(1) the existing helper's MLP model architecture is fundamentally wrong** — it treats permutation positions as ordinal integers instead of categorical variables, losing critical information; **(2) cayleypy has built-in MITM+beam search via `bfs_result_for_mitm` that no agent has used**; **(3) BFS to depth 6 produces 19.4M states with exact distances in ~1s, which is both a perfect training dataset and a MITM backstop**. These three insights combine into a concrete recipe that should dramatically outperform 44114.

---

## Finding 1: The Existing Helper's Model Architecture Is Wrong

**Relevance**: Any agent using `trained_predictor_beam_search.py` (idea_008, idea_003)
**Detail**: The `_PredictorMLP` class in `helpers/trained_predictor_beam_search.py` does this:

```python
def forward(self, x):
    if x.dtype != torch.float32:
        x = x.float()       # cast int64 → float32
    return self.net(x)       # pass raw 120 integers through linear layers
```

This treats each position in the 120-element state as an ordinal number, where value 119 is "close to" 118 and "far from" 0. But the state is a **permutation** — position 3 holding value 47 is categorically different from position 3 holding value 48, and there is no ordinal relationship. The built-in cayleypy `MlpModel` (in `cayleypy/models/models.py`) correctly handles this with one-hot encoding:

```python
def forward(self, x: torch.Tensor) -> torch.Tensor:
    x = nn.functional.one_hot(x.long(), num_classes=self.num_classes_for_one_hot)
    x = x.float().flatten(start_dim=-2)   # 120 ints → 120×120=14400 binary features
    return self.layers(x).squeeze(-1)
```

I ran a controlled experiment comparing both architectures:

| Architecture | Training Loss (20 epochs, 226k samples) | Params |
|---|---|---|
| Raw integer MLP (existing helper) | **4.57** | ~50k |
| Embedding-based MLP (120×32 embed) | **0.86** | ~1.2M |

The embedding model achieves **5.3× lower loss** with the same training data. The raw integer model cannot learn accurate distances because it's optimizing on a fundamentally wrong input representation.

**Actionable implication**: Replace the `_PredictorMLP` in the helper with either:
- (a) An embedding-based model: `nn.Embedding(120, 32)` per position → flatten → MLP. Memory-efficient during inference.
- (b) Use the built-in `MlpModel` via `ModelConfig(model_type='MLP', input_size=120, num_classes_for_one_hot=120, layers_sizes=[512, 256])`. This is what pretrained models for other puzzles (lrx-16, lrx-32) use.

Option (a) is recommended because it avoids the 14,400-wide one-hot tensor that causes OOM during beam search inference with large beams (see Finding 5).

---

## Finding 2: CayleyPy Has Built-In MITM+Beam Search — Never Used

**Relevance**: All solution agents using beam search

**Detail**: The `beam_search_simple` method in `cayleypy/algo/beam_search.py` accepts a parameter `bfs_result_for_mitm`:

```python
def search_simple(self, *, start_state, predictor=None, beam_width=1000, max_steps=1000,
                  return_path=False, bfs_result_for_mitm=None):
```

When provided, beam search terminates not only when it reaches the exact central state, but when it reaches **any state in the BFS neighborhood** precomputed from the central state. The path is then: beam_path + BFS_path_to_center. This effectively halves the required search depth.

The code at `beam_search.py:132-135`:
```python
bfs_layers_hashes = [graph.central_state_hash]
if bfs_result_for_mitm is not None:
    assert bfs_result_for_mitm.graph == graph.definition
    bfs_layers_hashes = bfs_result_for_mitm.layers_hashes
```

And the path length at `beam_search.py:167`:
```python
return BeamSearchResult(True, i + bfs_layer_id + 1, path, ...)
```

I verified this works: for sid=10 (depth 10), `beam_search(bfs_result_for_mitm=bfs_result)` with hamming predictor finds the optimal path (len=10), while without MITM it finds len=12. The MITM backstop saved 2 beam search steps.

**CRITICAL IMPLEMENTATION DETAIL**: The BFS result and the beam search MUST use the **same CayleyGraph instance** (or at least share the same hasher). The `StateHasher` uses random seeds, so a BFS computed on one graph instance cannot be used with beam search on a different instance — the hash values will mismatch and the intersection check silently fails. I verified this the hard way: BFS on `graph_cpu` + beam search on `graph_gpu` → all MITM queries return "not found" despite the states being present.

**Actionable implication**: Compute BFS on the same `CayleyGraph` object that beam search uses:
```python
graph = CayleyGraph(Puzzles.megaminx(), dtype=torch.int8)
bfs_result = graph.bfs(max_diameter=6, return_all_hashes=True, max_layer_size_to_explore=10**9)
# ... train predictor on same graph ...
graph.beam_search(start_state=state, predictor=predictor, bfs_result_for_mitm=bfs_result, ...)
```

---

## Finding 3: BFS Depth 6 = 19.4M Exact-Distance Training Samples in 1 Second

**Relevance**: Agents training predictors (idea_008, idea_003)

**Detail**: BFS from the central state to depth 6 produces these layer sizes:

| Depth | States | Cumulative | Growth Factor |
|---|---|---|---|
| 0 | 1 | 1 | — |
| 1 | 24 | 25 | 24× |
| 2 | 408 | 433 | 17× |
| 3 | 6,208 | 6,641 | 15.2× |
| 4 | 90,144 | 96,785 | 14.5× |
| 5 | 1,280,160 | 1,376,945 | 14.2× |
| 6 | 17,975,460 | 19,352,405 | 14.0× |

Key properties of this BFS data:
- **Every distance label is EXACT** (not overestimated like random walks)
- **All states are unique** (BFS deduplicates)
- **Covers the full neighborhood** (not a random sample)
- **Computed in ~1s on GPU**, ~14s on CPU

For comparison, `random_walks(width=50000, length=20, mode='bfs')` produces ~800k samples with distances 0-19, where some distances are overestimated because BFS width truncation causes some states to be lost.

Training on BFS data instead of random walk data gives:
- **Perfect distance labels** (0 MSE achievable)
- **24× more data** (19.4M vs 800k)
- **Zero overestimation noise**

Depth 7 is infeasible (~252M states, OOM on 16GB GPU). Depth 6 is the sweet spot.

**Actionable implication**: Replace `graph.random_walks(width=50000, length=20, mode='bfs')` with:
```python
bfs_result = graph.bfs(max_diameter=6, return_all_hashes=True,
                       max_layer_size_to_explore=10**9)
# Extract training data from BFS layers
X_list, y_list = [], []
for depth, layer_states in bfs_result.layers.items():
    X_list.append(layer_states)
    y_list.append(torch.full((len(layer_states),), depth))
X = torch.vstack(X_list)
y = torch.hstack(y_list).float()
```

Then use `bfs_result` as the MITM backstop AND `X, y` as training data. Two birds, one BFS.

---

## Finding 4: Memory-Efficient Model Architecture for Beam Search Inference

**Relevance**: Agents implementing trained predictor beam search

**Detail**: During beam search inference, the predictor is called on `layer2` which has up to `beam_width × n_generators` states before pruning. For beam_width=8192 and 24 generators, that's up to 196,608 states. The one-hot encoding of each state is 120×120=14,400 floats (57,600 bytes). For 196k states: 196,608 × 57,600 = **10.9 GB**. This causes OOM.

The Predictor class has a `batch_size` parameter (via `graph.batch_size`, default 2^20) that splits predictions into batches. Setting `graph.batch_size = 1024` reduces peak memory to 1024 × 57,600 = **56 MB per batch**. But this creates 192 batches, slowing inference.

A better approach: **use an embedding-based model** that avoids the 14,400-wide tensor entirely:

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
        x = self.embed(x.long()).flatten(start_dim=-2)  # (batch, 3840)
        return self.net(x).squeeze(-1)
```

Memory comparison for 196k states:
- One-hot: 196k × 14,400 × 4 = 10.9 GB → OOM
- Embedding (dim=32): 196k × 3,840 × 4 = 2.9 GB → feasible (but still tight)
- Embedding (dim=16): 196k × 1,920 × 4 = 1.4 GB → comfortable

With `graph.batch_size = 2048`, the embedding model (dim=32) uses only 2048 × 3840 × 4 = 30 MB per batch.

**Actionable implication**: Use `nn.Embedding(120, 16)` or `nn.Embedding(120, 32)` instead of one-hot encoding. Set `graph.batch_size = 2048` before beam search. This avoids OOM and allows beam_width up to 8192.

---

## Finding 5: Combined Recipe — BFS Training + Embedding MLP + MITM Beam Search

**Relevance**: The single highest-priority implementation for gen004

**Detail**: Combining Findings 1-4, the complete recipe is:

```python
import torch, torch.nn as nn
import cayleypy
from helpers.core import load_test

def entrypoint():
    gdef = cayleypy.Puzzles.megaminx()
    graph = cayleypy.CayleyGraph(gdef, dtype=torch.int8)
    graph.batch_size = 2048  # avoid OOM in predictor inference

    # Phase 1: BFS to depth 6 — training data + MITM backstop
    bfs_result = graph.bfs(max_diameter=6, return_all_hashes=True,
                           max_layer_size_to_explore=10**9)
    X_list, y_list = [], []
    for depth, layer_states in bfs_result.layers.items():
        X_list.append(layer_states)
        y_list.append(torch.full((len(layer_states),), depth, dtype=torch.float32))
    X = torch.vstack(X_list)
    y = torch.hstack(y_list)

    # Phase 2: Train embedding-based MLP
    model = EmbeddingMLP(embed_dim=32, hidden=[512, 256]).to(graph.device)
    # ... train with Adam, MSE, 30 epochs, batch_size=8192 ...
    predictor = cayleypy.Predictor(graph, model)

    # Phase 3: Solve each puzzle with predictor + MITM
    tests = load_test(proxy=True)
    results = {}
    for sid, state in tests.items():
        res = graph.beam_search(
            start_state=list(state), beam_width=4096, max_steps=200,
            return_path=True, predictor=predictor, beam_mode='simple',
            bfs_result_for_mitm=bfs_result,
        )
        if res.path_found and res.path is not None:
            moves = [_to_kaggle_name(gdef.generator_names[i]) for i in res.path]
            results[sid] = ".".join(moves)
        else:
            results[sid] = sample_paths.get(sid, "")  # fallback
    return results
```

**Why this should beat 44114:**
1. The predictor (trained on 19.4M exact-distance samples with proper categorical encoding) should guide beam search far better than hamming or unguided
2. MITM backstop reduces required beam depth by up to 6 steps, effectively multiplying search power
3. The model architecture correctly represents the permutation state space

**Estimated compute cost:**
- BFS: ~1s
- Training: ~60-120s (19.4M samples, 30 epochs, batch 8192)
- Per-puzzle beam search: ~1-5s for shallow, ~5-30s for medium, ~30-60s for hard
- Total for 101 proxy puzzles: ~5-15 minutes

**Risk**: For very_hard puzzles (depth 500-1000), even a perfect predictor with MITM depth 6 may not find solutions within max_steps=200. These puzzles still fall back to sample_submission. The score improvement comes primarily from solving short/medium/hard puzzles optimally instead of using sample_submission.

---

## Finding 6: Random Walk Mode Comparison

**Relevance**: Agents generating training data

**Detail**: The `random_walks()` method in cayleypy supports three modes:

| Mode | Description | Distance Accuracy | State Uniqueness |
|---|---|---|---|
| `classic` | Independent random walks | Overestimated (upper bound) | Duplicates common |
| `bfs` | BFS with width truncation | Near-exact (BFS ordering) | All unique |
| `nbt` | Non-backtracking beam-style | Better than classic | All unique |

The `bfs` mode is strictly better than `classic` for training data because:
- BFS ordering ensures states at distance d appear before d+1
- No duplicate states (cleaner gradients)
- Distances are closer to true optimal (BFS finds shortest paths first)

The `nbt` mode "mixes even faster" per the source code comments — it avoids backtracking by banning previously visited states across all trajectories. This could produce even better training data for deep distances.

**Actionable implication**: Always use `mode='bfs'` for training data generation. For better coverage of deep states, consider `mode='nbt'` with `nbt_history_depth=5`. But BFS depth-6 data (Finding 3) is superior to both because it provides exact distances.

---

## Finding 7: The Predictor Interface Contract

**Relevance**: Agents building custom predictors

**Detail**: From reading `predictor.py` source code, the Predictor class accepts:

1. `"zero"` — returns 0 for all states (unguided beam)
2. `"hamming"` — Hamming distance from central state
3. `torch.nn.Module` — calls `.eval()`, `.to(graph.device)`, then uses forward pass
4. Any object with `.predict()` method (e.g., sklearn models)
5. Any callable

The model receives **decoded states** (integer tensors, shape `[batch, 120]`, values 0-119) and must return a tensor of shape `[batch]` with **lower scores = closer to destination**. The Predictor handles batching via `graph.batch_size`.

**Important**: For option (3), the model is set to `eval()` mode and moved to `graph.device`. Make sure any custom model handles the device transfer correctly (e.g., embedding layers, batch norms).

**Actionable implication**: When building a custom predictor, the model's `forward(x)` must accept `torch.int64` tensors of shape `[batch, 120]` and return `float` tensors of shape `[batch]`. The input is raw decoded state (not encoded), and values are integers 0-119.

---

## Finding 8: Advanced Beam Mode Has No Path Return (Confirmed)

**Relevance**: All beam search agents

**Detail**: Confirmed from source code that `beam_search.py:270-273` in `search_advanced`:
```python
if flag_found_destination:
    if verbose >= 1:
        print(f"Found destination state at step {i_step}")
    return BeamSearchResult(True, i_step, None, ...)  # path is ALWAYS None
```

The advanced mode **always returns path=None**. This is not a bug per se — the advanced mode uses a different algorithm that doesn't track parent pointers. But it means the only useful mode is `'simple'`.

The `'advanced'` mode does support `history_depth` for non-backtracking, which could theoretically explore more states. But without path return, it's useless for our problem.

**Actionable implication**: Always use `beam_mode='simple'`. The `history_depth` parameter is only available in `'advanced'` mode and is therefore unusable.

---

## Finding 9: Interactive BFS for Synchronous Bidirectional Search

**Relevance**: Agents considering MITM for specific puzzles

**Detail**: CayleyPy has an `InteractiveBfs` class (`cayleypy/algo/interactive_bfs.py`) that computes BFS layers one at a time. Combined with `MeetInTheMiddle.find_path_between`, this enables synchronous bidirectional search:

```python
from cayleypy.algo.interactive_bfs import InteractiveBfs
from cayleypy.algo.bfs_mitm import MeetInTheMiddle

# Find shortest path between start and destination states
path = MeetInTheMiddle.find_path_between(graph, start_state, dest_state, max_diameter=D)
```

This computes BFS from both sides simultaneously and stops when they meet. For depth D puzzles, it explores ~2 × (states at depth D/2) instead of (states at depth D). This is more memory-efficient than one-directional BFS.

However, for the Megaminx, the growth factor is ~14× per level, so:
- `find_path_between` with `max_diameter=10` explores ~2 × 90k = 180k states total
- This finds optimal paths up to depth 20
- For depth 100, `max_diameter=50` would need ~2 × 24^25 ≈ astronomical states

**Actionable implication**: `MeetInTheMiddle.find_path_between` can optimally solve puzzles up to depth ~20 (short/medium buckets) without any ML. For deeper puzzles, it's infeasible. Use this as a fast path for shallow puzzles, then fall back to predictor+beam for deeper ones.

---

## Finding 10: The `find_path_from` Method for Pre-Computed BFS

**Relevance**: All agents using BFS-based approaches

**Detail**: `CayleyGraph.find_path_from(start_state, bfs_result)` finds the path from start_state to central state using a precomputed BFS result. This requires `bfs_result` to have been computed with `return_all_hashes=True`. The method works in O(diameter) time by checking hash membership layer by layer.

This means: if a puzzle state appears in the BFS depth-6 neighborhood, `find_path_from` returns the optimal path instantly (no search needed). For the proxy test set, any puzzle with depth ≤ 6 (ids 1-6, which are sid=0 and sid=10 since proxy takes every 10th) would be solved instantly.

**Actionable implication**: Before running beam search on any puzzle, first check `find_path_from`. If the state is in the BFS neighborhood, use the instant optimal path. Only run beam search if `find_path_from` returns None.

---

## Open Questions

1. **How much does the trained predictor + MITM actually improve over compression?** The individual components work (better model architecture, MITM backstop, exact training data), but the combined end-to-end pipeline hasn't been benchmarked on the full proxy. This is the experiment for gen004.

2. **What is the optimal beam_width × max_steps trade-off per bucket?** With the MITM backstop, beam search for depth-D puzzles only needs to reach depth D-6. This changes the beam width requirements significantly. For depth 50 puzzles with MITM depth 6: beam needs to reach depth 44, which is still very deep.

3. **Can we do multi-phase solving?** Phase 1: predictor+beam to get to depth ~30. Phase 2: use a different strategy (e.g., from the partial solution state, do another beam search with different parameters). This is related to iterative deepening.

4. **What embedding dimension is optimal?** I tested dim=32. Dim=16 is more memory-efficient. Dim=64 might learn better representations. This is a hyperparameter to tune.

5. **Can we train on BFS data + random walk data combined?** BFS gives exact distances up to depth 6. Random walks (mode='bfs', length=50) give approximate distances up to depth 50. A combined dataset could give the model both exact near-solved knowledge and approximate deep knowledge.

6. **Does the 14× per-level growth rate hold for deeper BFS?** If yes, then depth 7 ≈ 252M, depth 8 ≈ 3.5B. Even on CPU with 32GB RAM, depth 7 is borderline and depth 8 is infeasible.

7. **What do Kaggle top solutions actually use?** I couldn't access the actual notebook code. The 13-vote notebook (mitchell11/cayleypy-megaminx-first-steps) describes the MLP recipe but not the winning architecture/training details. The competition's top solutions likely use larger models, more training data, or novel approaches not visible in public notebooks.
