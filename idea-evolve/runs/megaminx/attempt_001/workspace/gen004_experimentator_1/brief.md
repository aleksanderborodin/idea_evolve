## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py` → fitness **44094** (predictor+compression, suffix-optimized).
Compression-only floor: 44114.
Target: **15000 proxy**.

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/helpers/README.md` — current helper index and caveats
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/helpers/trained_predictor_beam_search.py` — the broken helper (raw-integer MLP)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_011.md` — correct embedding-MLP architecture and evidence
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_010.md` — BFS depth-6 data (19.4M samples, ~1s)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_012.md` — built-in MITM via `bfs_result_for_mitm`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/feedback/system_recommendations.md` — REC-3 is your task (fix or replace the helper)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/reports/gen003/research_1.md` — full code snippets and verified pipeline

## Directive

**Build a corrected, well-tested helper for the combined-recipe pipeline (idea_013).** The existing `helpers/trained_predictor_beam_search.py` uses the wrong model architecture (raw-integer MLP, 5.3× worse loss than embedding) and does not use `bfs_result_for_mitm`. This helper has actively blocked 2 generations of predictor work. Your output is a replacement.

### Scope (strictly bounded — do not expand)

You write ONE file to `output/helpers/embedding_predictor_beam.py` exposing a single
entry-point function:

```python
def solve_with_embedding_predictor(
    states: dict[int, tuple],      # {sid: state tuple}
    *,
    beam_width: int = 4096,
    max_steps: int = 200,
    embed_dim: int = 32,
    hidden_dims: tuple = (512, 256),
    epochs: int = 30,
    batch_size: int = 8192,
    lr: float = 1e-3,
    train_depth: int = 6,          # BFS max_diameter
    fallback_paths: dict[int, str] | None = None,   # per-sid compression fallback
    device: str = "cuda",
    verbose: bool = False,
) -> tuple[dict[int, str], dict]:
    """Returns (paths_by_sid, diagnostics). diagnostics contains:
       train_loss, train_time_s, bfs_time_s, search_time_s, solved_count,
       fallback_count, beam_depth_stats.
    """
```

Internally the helper must:
1. Build a fresh `cayleypy.Puzzles.megaminx()` CayleyGraph on `device`.
2. Compute `bfs_result = graph.bfs(max_diameter=train_depth, return_all_hashes=True, max_layer_size_to_explore=10**9)`.
3. Assemble `(X, y)` from `bfs_result.layers` per idea_010.
4. Train an `EmbeddingMLP(state_size=STATE_SIZE, num_classes=STATE_SIZE, embed_dim=embed_dim, hidden_dims=hidden_dims)`.
5. Wrap with `cayleypy.Predictor(graph, model)`.
6. For each `(sid, state)`, run `graph.beam_search(..., predictor=..., bfs_result_for_mitm=bfs_result, beam_mode='simple', return_path=True)`; on `None`, fall back to `fallback_paths[sid]` if supplied, otherwise leave empty (caller handles).
7. Return paths as dot-joined Kaggle-style move names (use `GENERATOR_NAMES` from `helpers.core` to translate cayleypy move names back).

### Milestone Protocol (mandatory)

- **Milestone 1 (~20 min).** Write the helper and write a **self-contained test** (`output/test_embedding_predictor.py`) that imports it, runs it on **exactly 3 puzzles** from `load_test(proxy=True)` (pick sid=0, sid=10, sid=100), and prints `diagnostics`. This is your first scored output. It does NOT go into `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/` — it is the helper deployment artefact.
- **Milestone 2 (~15 min).** Run the test. If any crash, fix and rerun. Keep iterating until the test prints non-empty paths for all 3 puzzles and at least one path from beam search (not fallback).
- **Milestone 3 (remaining).** Optionally produce `output/sol01.py` that calls the helper on the full proxy set with `fallback_paths` loaded from `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/rank02_44114.py`'s compression function. Score it. This becomes a population solution AND acts as a correctness check for the helper.

### Validation contract (orchestrator will enforce)

Your helper must:
- Import successfully in a fresh Python process (no top-level side effects — all work inside the function).
- Only import from stdlib, `torch`, `torch.nn`, `cayleypy`, and `helpers.core`. No network calls, no disk writes outside the returned diagnostics.
- Pass a simple smoke test: `from helpers.embedding_predictor_beam import solve_with_embedding_predictor; paths, diag = solve_with_embedding_predictor({0: load_test(True)[0]}, epochs=2, max_steps=20)` must return in under 120 s.

### Known pitfalls (from research_1 and prior failures)

- **Same graph instance for BFS and beam search.** Hash seeds are random per-graph — BFS on one graph instance, beam on another → silent MITM miss. Build ONE graph and pass it (or keep as module-level).
- **State dtype on CUDA.** States must be int8/int64 tensors on CUDA. Do NOT cast to float before passing to beam_search (triggers `rshift_cuda` error). Your embedding layer does the `.long()` cast internally.
- **`beam_mode='advanced'` is broken.** Always use `'simple'`.
- **Move name translation.** cayleypy may return moves named `M_U`, `M_U_inv`, etc. Kaggle expects `U`, `-U`. Use `GENERATOR_NAMES` from `helpers.core` and translate via the graph's move-name attribute (check `graph.generator_names` or similar — research_1 discussed this).
- **`random_walks` kwargs are keyword-only.** Not relevant here (you use BFS), but noted for completeness.

### Deliverables checklist

- [ ] `output/helpers/embedding_predictor_beam.py` — the helper
- [ ] `output/test_embedding_predictor.py` — smoke test that exits 0 on success
- [ ] `output/sol01.py` (optional, nice-to-have) — full-proxy call using the helper
- [ ] `output/report.md` — includes: final training loss on the 3-puzzle run, whether move-name translation was needed, and any API quirks you hit. Explicitly state whether the orchestrator should promote the helper (i.e. whether your test passed cleanly).

### What you are NOT doing

- Not fixing the existing `trained_predictor_beam_search.py`. Write a new file. The old one stays — it will be deprecated by the Evaluator after your helper is validated.
- Not chasing non-embedding architectures (GNN, transformer, etc.). explore_1 is doing that.
- Not extending the helper beyond the single entry-point above. Scope creep is how gen003 experimentator timed out with zero output.
