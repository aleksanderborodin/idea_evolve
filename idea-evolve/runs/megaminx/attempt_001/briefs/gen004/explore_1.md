## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py` → fitness **44094**.
Compression-only floor: 44114 (every top solution converges here).
Target: **15000 proxy**.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/state_of_affairs.md` — ground truth
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_011.md` — embedding MLP (what exploit_1 is using; you must NOT use this)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_010.md` — BFS training data (you MAY reuse this — BFS data is universal)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/patterns/confirmed/pattern_006.md` (if exists) — raw-integer MLP is ineffective
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/description.md` — problem spec
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/helpers/README.md` — helper index

## Directive — Track B RADICAL EXPLORATION

**This is a Track B radical exploration. You must NOT use a flat MLP predictor of any flavor (raw-integer, embedding, MLP-Mixer, etc.). You must NOT start from `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py`, any file in `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/`, or refine any existing solution. Start from scratch.**

Your mission: **test whether a Graph Neural Network predictor can capture Cayley-graph structure that flat MLPs cannot**. This is open question #6 in the State of Affairs, never investigated.

### Why GNN, specifically

- Megaminx state is a permutation: 120 cells, each holding an integer label 0..119. There is latent graph structure — the 24 generators define a *fixed* connectivity pattern over cells (each generator is a 5-cycle, so each cell is connected to a small set of other cells under every generator). Flat MLPs see the permutation as a flat vector; a GNN can see the adjacency.
- `cayleypy.Predictor` accepts **any** `nn.Module`. There is no architectural constraint preventing a GNN from being plugged into beam search.
- research_1 and explore_2 mentioned GNN predictors speculatively but nobody tested them. If the flat embedding MLP (idea_011) tops out at a plateau, a structured predictor may keep improving.

### The concrete idea

Build a small GNN predictor that:
1. Treats the 120 cells as graph nodes with node features = the current value at that cell (via `nn.Embedding`).
2. Uses the **generator-induced adjacency**: for each of the 24 generators, each cell has up to 24 "generator-neighbour" cells (the cells its value reaches after applying each generator once). Construct a fixed `edge_index` tensor of shape `[2, E]` covering this union graph.
3. Applies 2–4 GCN/GIN/GAT layers to propagate information between neighbouring cells. `torch_geometric` is fine if available; if not, implement message passing by hand with scatter_add (it's ~20 lines).
4. Pools node features (mean, max, or both concatenated) and passes through a small MLP head to predict distance-to-solved.

### Milestone Protocol (mandatory)

- **Milestone 1 (first ~30 min) — produce `output/sol01.py` that at MINIMUM runs the compression baseline (import from `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/rank02_44114.py`)** so you have a scored sol01 no matter what. Then BEGIN building the GNN. This guarantees non-zero output.
- **Milestone 2 (~45 min).** Train the GNN on BFS depth-6 data (reuse idea_010 — the BFS is free, ~1s). Target: train loss < 1.5 on 1M samples (compare to embedding MLP's 0.86; you are not trying to beat it yet, just to prove the architecture trains). Wrap in `cayleypy.Predictor`, run beam search on a single puzzle (sid=10), confirm it returns a valid path. Save as `output/sol02.py` only if the beam-search-guided-by-GNN actually works end-to-end on ≥1 puzzle.
- **Milestone 3 (remaining).** Full-proxy evaluation with GNN + compression fallback. Score it. Report honestly — if GNN does not beat embedding MLP, that's a valid negative result (pattern_XXX: "GNN predictors do not outperform embedding MLP on Megaminx at training-depth 6").

### Concrete starting point

```python
import torch, torch.nn as nn, torch.nn.functional as F
import cayleypy
from helpers.core import STATE_SIZE

# 1) Build graph + BFS (reuse idea_010)
gdef = cayleypy.Puzzles.megaminx()
graph = cayleypy.CayleyGraph(gdef)
bfs_result = graph.bfs(max_diameter=6, return_all_hashes=True,
                       max_layer_size_to_explore=10**9)

# 2) Construct generator-induced adjacency once (120x120)
# Each generator g is a length-120 permutation. Edge (i, g[i]) for all i.
# Take union over all 24 generators, deduplicate, make undirected.
generators = gdef.generators  # check exact attribute name
edge_set = set()
for perm in generators:
    for i in range(STATE_SIZE):
        edge_set.add((i, perm[i]))
        edge_set.add((perm[i], i))
edge_index = torch.tensor(list(edge_set), dtype=torch.long).t().cuda()

# 3) A minimal message-passing GNN (no external deps)
class SimpleGNN(nn.Module):
    def __init__(self, num_classes=120, embed_dim=32, hidden=64, n_layers=3):
        super().__init__()
        self.embed = nn.Embedding(num_classes, embed_dim)
        self.layers = nn.ModuleList([
            nn.Linear(embed_dim if i == 0 else hidden, hidden)
            for i in range(n_layers)])
        self.head = nn.Sequential(nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))
    def forward(self, x, edge_index):
        # x: (B, 120) int
        h = self.embed(x.long())                # (B, 120, embed_dim)
        for lin in self.layers:
            src, dst = edge_index[0], edge_index[1]
            msg = h[:, src] + h[:, dst]         # naive sum message
            agg = torch.zeros_like(h)
            agg.index_add_(1, dst, msg)
            h = F.relu(lin(agg))
        return self.head(h.mean(dim=1)).squeeze(-1)
```

### Off-limits (do NOT do)

- **No flat MLP baselines.** exploit_1 is running the embedding MLP. Running your own flat MLP is a wasted comparison.
- **No compression-only solutions.** Compression is solved (7 solutions at 44114). Use it only as a fallback for puzzles GNN+beam fails.
- **No predictor-free beam search.** Unguided beam search is a confirmed dead end (SoA dead-end #1).
- **No Hamming predictor.** Debunked (idea_006, pattern_006).
- **No `beam_mode='advanced'`.** Known broken.

### Deliverable

At least `output/sol01.py` (compression fallback, guaranteed to score 44114). Ideally `output/sol02.py` (GNN-guided beam search). The `output/report.md` must state:
- Whether the GNN trained (final loss).
- Whether beam search with GNN predictor completed on ≥1 puzzle.
- Per-bucket breakdown from the best scored solution.
- **Verdict:** does GNN look promising, inconclusive, or dead? Be blunt — negative results are valuable.
