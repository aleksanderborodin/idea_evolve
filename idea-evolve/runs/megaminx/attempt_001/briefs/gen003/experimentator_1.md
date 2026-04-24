## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py` → fitness 44114 (compression_ratio=0.8723)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/top/rank02_44114.py`
Best from gen002: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen002/explore_2/sol01.py` → fitness 44114

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_008.md` — Trained MLP predictor pipeline
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/knowledge/ideas/active/idea_003.md` — Predictor-guided beam search
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/helpers/README.md` — Current helper documentation
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx/helpers/core.py` — Existing helpers (cayleypy_beam_solver, etc.)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen002/exploit_1/sol02.py` — Previous exploit that hit state encoding error

## Directive

**Build a `trained_predictor_beam_search` helper** that packages the full ML pipeline into a reusable function. This addresses REC-1 and REC-2 from the system critic: every agent that tries the predictor route hits the same state-encoding friction. A single working helper unlocks the primary path for all future agents.

**Deliverable**: `output/helpers/trained_predictor_beam_search.py` containing:

```python
def trained_predictor_beam_search(
    state,                           # starting state (tuple/list of 120 ints)
    graph=None,                      # optional pre-built CayleyGraph
    n_walks=50000,                   # training data size
    walk_length=20,                  # random walk depth for training
    beam_width=4096,                 # beam search width
    max_steps=80,                    # max beam search depth
    hidden_dims=(256, 128),          # MLP architecture
    epochs=10,                       # training epochs
    device=None,                     # auto-detect if None
) -> tuple:
    """
    Train a tiny MLP on random walks and run predictor-guided beam search.
    
    Returns: (path_str, result_object)
    - path_str: dot-joined move string if solved, else None
    - result_object: the raw beam_search result for diagnostics
    
    Raises RuntimeError if state encoding fails.
    """
```

**Implementation requirements:**

1. **Device handling**: Auto-detect CUDA, ensure model and tensors are on the same device. The `rshift_cuda` error from gen002 exploit_1 was caused by float/int8 mismatch.

2. **State encoding**: The input `state` is a tuple/list of 120 ints. Convert to the correct dtype for CayleyGraph (int8). Handle the conversion explicitly — this is where previous agents failed.

3. **Training loop**: Simple MSE loss. Log training progress (epoch, loss) so agents can see if the model is learning.

4. **Beam search call**: Use `beam_mode='simple'` exclusively (advanced mode has path-return bug). Handle `path_found=True` but `path=None` gracefully.

5. **Error handling**: Wrap the beam_search call in a try/except. If it fails, return a meaningful error message, not a silent None.

6. **Import structure**: Use `import cayleypy` and `import torch` at the top. The helper will be deployed to `problems/megaminx/helpers/`.

**After building the helper, validate it** by running a quick smoke test:
```python
# Smoke test on a shallow puzzle
result = trained_predictor_beam_search(solved_state_after_few_moves)
```

If the helper works, **also write a solution** (`output/sol01.py`) that uses it on the proxy test set and evaluate it. The helper + a scored solution would be the ideal outcome.

**Note on constraints**: The helper must have NO top-level side effects (no code that runs on import). All logic inside functions. No network access. Only standard library + torch + cayleypy imports.
