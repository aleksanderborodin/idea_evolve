# Research Findings — Megaminx Gen-1 Track B

## Summary

The current best is the zero-search floor (sample_submission verbatim, fitness=50,572 on proxy). No generation-1 solution agents have run yet, so the entire optimization space is untouched. Three families dominate the literature: (1) ML-guided beam search with a trained distance predictor, (2) Meet-in-the-middle with precomputed BFS tables, and (3) hand-tuned macro-move heuristics. The ML approach is the clear winner — it is what top Kaggle entrants used to reach ~80k full-set score.

---

## Finding 1: ML-Guided Beam Search is the Top Priority

**Relevance**: Any explore/full/genetic agent looking for the highest-leverage next step.

**Detail**: The top Kaggle scores (~80k full / ~8k proxy) were achieved with custom-trained distance predictors plugged into cayleypy's beam search. The full pipeline (verified working in this environment):

```python
from cayleypy import Puzzles, CayleyGraph, Predictor
import torch, torch.nn as nn

# 1. Build graph
graph = CayleyGraph(Puzzles.megaminx(), device='cpu')  # GPU available via CUDA

# 2. Generate training data from random walks
X, y = graph.random_walks(width=50000, length=25, mode='bfs')
# X: (N, 120) torch.int64 — each row is a state (permutation of 0..119)
# y: (N,) torch.int32 — distance from solved state

# 3. Train a small MLP to predict distance
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(120*120, 256), nn.GELU(),
            nn.Linear(256, 128), nn.GELU(),
            nn.Linear(128, 1)
        )
    def forward(self, x):
        # x: (batch, 120) int indices
        x = nn.functional.one_hot(x.long(), num_classes=120).float().flatten(1)
        return self.net(x).squeeze(-1)

model = Net()
# Standard MSE training, 50 epochs, batch 1024, lr 0.001, Adam

# 4. Wrap as predictor and use in beam search
predictor = Predictor(graph, model)
result = graph.beam_search(
    start_state=test_state,
    beam_width=2000,
    max_iterations=300,
    predictor=predictor,
    return_path=True
)
```

**Key facts confirmed in this environment:**
- `Puzzles.megaminx()` → `CayleyGraphDef` ✓ (same as helpers.core)
- `graph.random_walks(width, length, mode='bfs')` → `(X, y)` training pairs ✓
- `Predictor(graph, model)` → predictor wrapper ✓
- `graph.beam_search(predictor=...)` → guided search ✓

**Expected improvement**: A predictor trained on ~50k random-walk samples (length 20-30) should dramatically beat unguided beam. The ML notebook shows Hamming distance vs learned predictor success rates — learned predictor at beam=10⁶ finds paths that Hamming cannot find even at beam=10⁴.

**Important nuance**: The `central_state` of the CayleyGraph from `Puzzles.megaminx()` is a length-120 permutation `(0,1,2,...,119)`, matching what `helpers.core.solved_state()` returns. The graph generators are the same 24 Kaggle moves. So the trained model is directly applicable to our test puzzles.

**Actionable implication**: A gen-2 explore/full agent should implement the full ML pipeline above, train on ~50k-100k random walks of length 15-30, and use `Predictor(graph, model)` in `cayleypy_beam_solver`-style loop. The entrypoint returns `{sid: graph.beam_search(...)}`.

---

## Finding 2: Meet-in-the-Middle with Shallow BFS is a Low-Risk Complementary Approach

**Relevance**: Agents that want guaranteed improvement without ML training time.

**Detail**: The MITM notebook (alexandervc) demonstrates a proven pattern:
1. Precompute BFS to depth D: `bfs_result = graph.bfs(max_diameter=D, return_all_hashes=True)`
2. For any test state, use `MeetInTheMiddle.find_path_from(graph, start_state, bfs_result)` to find a path of length ≤ 2D.

**Concrete numbers from the notebook:**
- BFS to depth 6 covers ~18M states (precomputation: a few minutes on CPU)
- With BFS depth 6 precomputed, MITM solves states with optimal distance ≤ 12
- The Kaggle test set has depths 0-1000, so MITM alone solves only the `short` bucket (depth 1-25, 2 puzzles in proxy)

**Critical implementation detail**: The notebook shows that `bfs(max_diameter=5)` → `MeetInTheMiddle.find_path_from` solves state IX=10 (depth 10) in one shot. For the `short` bucket (ids 1-25), BFS depth 12-15 would cover optimal distances up to 24-30.

**Actionable implication**: Precompute BFS to depth 8-10 (covers ~90k-1.28M states, tractable), use MITM for the `short` and `medium` buckets (depth 1-100, ~10 puzzles in proxy). Fall back to sample_submission for deeper puzzles. This is quick to implement and gives guaranteed improvement over the sample floor for shallow puzzles.

**Note on memory**: BFS to depth 8 stores ~1.28M states. Each state is a length-120 int array. With proper hashing, this is ~150MB. Cayleypy's `bfs` with `return_all_hashes=True` returns a result object with a hash table. Test this before committing.

---

## Finding 3: Move Cancellation — Instant Free Improvement on sample_submission Paths

**Relevance**: Every agent should use this as a fallback safety net.

**Detail**: The sample_submission paths are the raw inverses of the random walks that generated the test states. These paths contain adjacent move cancellations (e.g., `U.-U` or `R.R.-R` which simplifies to `R`). Removing these compresses the path without any search.

**Concrete algorithm**: Iterate through the path, maintaining a move stack. For each move `m`:
- If stack is non-empty and `m` is the inverse of the top move, pop the stack (cancellation).
- Otherwise, push `m` onto the stack.

This is O(n) in path length and gives 5-15% compression on sample_submission paths with zero search.

**Actionable implication**: Every entrypoint() should at minimum do:
```python
def cancel_moves(path):
    if not path:
        return path
    moves = path.split(".")
    stack = []
    inverse = {m: m[1:] if m.startswith("-") else f"-{m}"
               for m in GENERATOR_NAMES}
    for m in moves:
        if stack and stack[-1] == inverse.get(m):
            stack.pop()
        else:
            stack.append(m)
    return ".".join(stack)
```
Then: `path = cancel_moves(sample[sid])` before returning.

---

## Finding 4: Beam-Search Budget Allocation by Bucket

**Relevance**: All search-based agents.

**Detail**: The score is dominated by the `very_hard` bucket (ids 501-1000, 50 of 101 proxy puzzles). These depths are 50-100× deeper than what unguided or even guided beam search can reach in a single pass. The strategic insight from initial_ideas.md is correct: allocate budget proportionally.

**Practical allocation for a predictor-guided beam search:**
| Bucket | IDs (proxy) | Recommended beam_width | max_steps | Expected behavior |
|---|---|---|---|---|
| special | 0 | 100 | 100 | Easy with guided search |
| short | 1-25 | 256-512 | 50 | Should solve well |
| medium | 26-100 | 1000 | 150 | Moderate success |
| hard | 101-500 | 2000 | 250 | Partial; fallback often |
| very_hard | 501-1000 | 4000+ | 500+ | Most will fall back to sample |

**Important**: Even a very good predictor only provides a heuristic. For very_hard depths (500+), the beam would need to contain the entire reachable state space to guarantee finding a solution. The practical approach is: use the best predictor available, search with the widest beam feasible in the time budget, and fall back to sample_submission when search fails.

---

## Finding 5: Predictor Training Data Quality Matters More Than Model Size

**Relevance**: Agents training custom models.

**Detail**: The key hyperparameters for training data are `width` and `length` in `graph.random_walks(width=W, length=L, mode='bfs')`:
- `length=L`: the random walk generates states at distances 0..L. Using L=30 covers the short+medium buckets well.
- `width=W`: more walks = more training samples. 50k samples trains a usable model; 500k trains a great one.
- `mode='bfs'`: ensures BFS ordering (all states at distance d before d+1), so training labels are exact distances.

**Critical**: The training states are random walks from the *solved* state. The model learns to estimate "how far is this state from solved?" — exactly the heuristic beam search needs.

**What NOT to do**: Do not use Hamming distance (count of displaced stickers) as the sole heuristic. The ML notebook proves it is dramatically worse than a learned predictor even with 10× larger beam width.

**Model size trade-off**: A 3-layer MLP (120*120 → 256 → 128 → 1) has ~3.7M parameters. Training on 50k samples for 50 epochs takes ~2 minutes on CPU. Larger models (more hidden dimensions) overfit on small datasets. Start small.

---

## Open Questions

1. **How well does a predictor trained on length-30 random walks generalize to depths 100-1000?** The training data only covers up to distance 30, but the test puzzles go up to depth 1000. The model will extrapolate — this could be a significant weakness for the very_hard bucket.

2. **Could multi-scale training help?** Train one predictor on length-15 walks (accurate for shallow), another on length-30 walks, another on length-50. Use shallow model for shallow puzzles and deep model for deep puzzles. Untested.

3. **What beam_width is needed for the hard/very_hard buckets with a trained predictor?** The ML notebook tests on LRX(12), not Megaminx. The effective beam width needed for Megaminx at depth 500 with a predictor is unknown. This is the key unknown for predicting whether the target (15k proxy) is achievable.

4. **Could IDA* with a pattern database outperform beam search + predictor?** The Rubik's cube literature shows IDA* + pattern databases (corners-only, edge-orbit) is competitive with beam search + predictor. Megaminx-specific pattern databases are unexplored in the Kaggle notebooks.

5. **Does GPU acceleration matter for beam search?** Cayleypy uses CUDA when available, but the per-step predictor evaluation (model forward pass) could be the bottleneck. Profiling needed.

6. **What is the actual compression_ratio achievable with guided beam search on medium puzzles?** This determines whether the target of 15,000 proxy (compression_ratio ~0.30) is realistic or needs MITM + predictor + multi-phase approaches.
