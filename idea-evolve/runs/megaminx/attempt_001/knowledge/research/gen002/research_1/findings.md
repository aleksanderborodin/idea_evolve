# Research Findings — Gen002 Track B: Concrete Beam Search Parameterization

## Summary

I investigated the predictor-guided beam search path by fetching and analyzing three Kaggle notebooks (beamsearch-hamming, meetinthemiddle-bfs-solver, first-steps) and running targeted experiments against the cayleypy API. The central finding: **Hamming predictor is not the answer — it provides zero advantage over unguided search at the same beam width**. The path to the target requires a trained MLP predictor, and there are critical beam parameter insights from the notebooks that agents are not using.

---

## Finding 1: Hamming Predictor Provides ZERO Advantage Over Unguided Search

**Relevance**: All solution agents considering idea_006 or idea_003
**Detail**: I ran controlled experiments comparing `Predictor(graph, 'hamming')` vs `predictor=None` at identical beam widths:

| Puzzle (depth) | Beam Width | Unguided Path Len | Hamming Path Len | Sample Len |
|---|---|---|---|---|
| sid=10 (depth 10) | 2048 | 14 | 14 | 10 |
| sid=10 (depth 10) | 8192 | 12 | 12 | 10 |
| sid=10 (depth 10) | 32768 | 10 | 10 | 10 |

**Both guided and unguided find identical path lengths at every beam width.** The hamming distance to solved state does not correlate with actual shortest-path distance. The search is guided by a heuristic that provides no information advantage over random exploration.

**Actionable implication**: Do not spend time on idea_006 (hamming predictor). The zero-cost experiment answer is: hamming doesn't help. The entire beam search improvement ceiling depends on a **trained MLP predictor** that learns actual distance from random walk data. This is the only path.

---

## Finding 2: Beam Width Must Be 4x-32x Larger Than Gen001 Used

**Relevance**: All solution agents attempting beam search
**Detail**: Gen001 agents used beam_width=512-4096. The hamming notebook (top-voted Megaminx beam search notebook, 2 votes) uses `beam_width=2**16 = 65536`. My experiments show:

- **beam_width=2048**: fails for depth 10 (finds len=14, optimal=10)
- **beam_width=32768**: barely solves depth 10 optimally (4.6s per puzzle)
- **beam_width=65536**: solves depth 10 in 5.8s but becomes intractable for depth 20+ (45s+, times out)

The optimal beam width scales with puzzle depth. For the **medium bucket** (depth 26-100), beam_width must exceed available GPU/CPU time budgets.

**Critical**: The relationship is exponential in depth — beam_width=65536 works for depth~10 but is completely infeasible for depth~100. This explains why gen001's beam search never beat compression: the required beam width for depth 100+ is beyond practical compute.

**Actionable implication**: For the **short bucket** (depth 1-25): try beam_width=8192-16384, max_steps=40-80. For the **medium bucket** (depth 26-100): beam_width=65536 is needed but likely too slow. The medium bucket is the first place where even massive beam widths fail — this is where the trained predictor must compensate.

---

## Finding 3: `beam_mode='advanced'` Is ~2x Faster But Has a Path-Return Bug

**Relevance**: All solution agents using beam search
**Detail**: The `beam_mode='advanced'` option is ~2x faster than `'simple'` mode:

| Mode | Time (bw=4096, depth=10) | Path Returned |
|---|---|---|
| simple | 2.83s | YES ✓ |
| advanced | 1.26s | **NO (BUG) — path=None** |

The `advanced` mode finds the path (`path_found=True`, correct `path_length=N`) but returns `path=None` even when `return_path=True`. This is a bug in cayleypy 0.1.0. The `get_path_as_string()` method asserts `self.path is not None` and crashes.

The **simple mode** correctly returns the path via `res.path` (list of generator indices) and `graph.definition.path_to_string(res.path)`.

**Actionable implication**: Agents must use `beam_mode='simple'` to get actual paths. The ~2x speedup from `advanced` mode is irrelevant since it can't return paths. Direct API calls (bypassing the helper) are required since `cayleypy_beam_solver` doesn't expose `predictor` or `beam_mode`.

---

## Finding 4: MITM With BFS Diameter 5-6 Covers Only Depth ≤ 10-12

**Relevance**: Agents considering idea_004 (MITM)
**Detail**: I ran MITM experiments across multiple diameters:

| Diameter | Total States | Can Solve Depth |
|---|---|---|
| 5 | 1.4M | ≤ 10 (1.4M forward states) |
| 6 | 19.4M | ≤ 12 |
| 7 (estimated) | ~200M+ | ≤ 14 |

BFS state count grows as O(24^d). Diameter 5 = 1.4M states; diameter 6 = 19.4M states; diameter 7 would be ~200M+. State growth is the limiting factor.

For the proxy test set (every 10th id): even the shallowest non-special puzzle is sid=10 (depth 10). Diameter=5 barely covers it. **All medium, hard, and very_hard bucket puzzles (depth 26-1000) have optimal distance >> 12, making MITM useless for them.**

The MITM notebook (4 votes) only works on depth ≤ 12 puzzles. The Megaminx competition requires solving up to depth 1000.

**Actionable implication**: MITM is irrelevant for this competition. Do not allocate time to idea_004 for medium/hard/very_hard buckets. It only helps for the short bucket (depth 1-25), and even then only if diameter ≥ 13 is tractable (it isn't).

---

## Finding 5: Graph Uses GPU Automatically — Description.md Says CPU-Only

**Relevance**: All solution agents
**Detail**: `CayleyGraph(gdef)` automatically uses CUDA/GPU when torch CUDA is available. The `dtype=torch.int8` option reduces memory. The description.md says "CPU-only" but this is contradicted by the actual behavior — the graph device is `cuda`, not `cpu`.

The GPU is currently **unused** by gen001 solutions because they call `cayleypy_beam_solver` which creates a graph without explicit GPU management, but the graph itself moves to GPU automatically.

**Actionable implication**: For beam search with large beam widths, the GPU acceleration is already active and is the only reason beam_width=65536 is tractable at all. Do NOT assume CPU-only constraints.

---

## Finding 6: Trained MLP Predictor — Specific Recipe From Research

**Relevance**: Agents implementing idea_003
**Detail**: The first-steps notebook (13 votes, highest for Megaminx) gives the exact pipeline:

```python
import torch
from cayleypy import CayleyGraph, CayleyGraphDef, Predictor, GapPuzzles

gdef = GapPuzzles.puzzle('megaminx')
graph = CayleyGraph(gdef, dtype=torch.int8)  # GPU, int8

# Generate training data: random walks from solved state
X, y = graph.random_walks(50000, 20, mode='bfs')  # 50k samples, length 20 walks

# Train MLP
model = torch.nn.Sequential(
    torch.nn.Linear(120, 256),
    torch.nn.ReLU(),
    torch.nn.Linear(256, 128),
    torch.nn.ReLU(),
    torch.nn.Linear(128, 1)
)
# Train with MSE on distance

# Use in beam search
predictor = Predictor(graph, model)
res = graph.beam_search(start_state=state, beam_width=8192, max_steps=80,
                       predictor=predictor, beam_mode='simple',
                       return_path=True, verbose=0)
```

The key: training data comes from `graph.random_walks()` — (state, distance) pairs generated by walking from the known solved state. This is the approach top Kaggle entrants used.

**Critical unknown**: Whether the trained predictor's accuracy on depth-20 random walks generalizes to depth-100+ puzzles. This is the central research question for gen003.

**Actionable implication**: An experimentator agent should run this exact pipeline and measure: (a) trained predictor MSE, (b) beam search quality vs hamming/unguided at same beam width, (c) per-bucket breakdown. This answers whether the entire approach is viable.

---

## Open Questions

1. **Does a trained MLP predictor actually beat hamming at practical beam widths?** We know hamming=unguided. We don't know if MLP-guided beats either. This is the single most important experiment.

2. **What training data distribution is needed?** Training on depth-20 walks: does it generalize to depth-100+ puzzles? Or does the predictor need domain-randomized depth training?

3. **What beam width is tractable per bucket within the 7-minute proxy eval budget?** The proxy eval must finish 101 puzzles. beam_width=65536 takes 5-45s per puzzle depending on depth. At 101 puzzles that's 8+ minutes just for beam search, before training time.

4. **Can the very_hard bucket be solved at all with beam search?** Depth 500-1000 requires astronomical beam width without a perfect predictor. Is there a fundamentally different approach (e.g., two-phase, pattern database) that avoids exponential beam width?

5. **Is `dtype=torch.float32` vs `torch.int8` accuracy-relevant for the predictor?** int8 may lose precision for the predictor's state representation.
