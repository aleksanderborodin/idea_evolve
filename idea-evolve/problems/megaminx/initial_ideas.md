---
name: sample_submission_fallback
lifecycle: active
confidence: high
cluster: baselines
supported_by: [baseline_submission.py, initial_facts.md#scramble_depth_equals_id]
contradicted_by: []
related_ideas: [cayleypy_beam_search, budget_aware_per_bucket]
---

# sample_submission as a guaranteed-valid fallback

`helpers.core.load_sample_submission_paths()` returns Kaggle's provided
sample paths — **every one is valid** (confirmed by data inspection and
the `cayleypy-megaminx-first-steps.ipynb` hint). Path length equals
scramble depth equals `initial_state_id` (for ids 1..1000).

Use this as a **safety net** in every solution:

```python
def entrypoint():
    from helpers.core import load_test, load_sample_submission_paths, is_solved, apply_path
    sample = load_sample_submission_paths()
    tests = load_test(proxy=True)
    out = {}
    for sid, state in tests.items():
        # Try your fast/cheap/clever search first
        path = my_search(state, budget_hint=sid)  # budget grows with depth
        # Verify; fall back to sample if broken or worse
        if path and is_solved(apply_path(state, path)) and len(path.split(".")) <= len(sample[sid].split(".")):
            out[sid] = path
        else:
            out[sid] = sample[sid]
    return out
```

The floor this buys you is `compression_ratio = 1.0` on puzzles you can't
improve. Every real optimization move (compression_ratio < 1.0) is a win
stacked on top of the freebie; no move is a regression.

**Sub-ideas worth exploring:**

- Per-puzzle budget tuned to depth: shallow puzzles deserve heavy search
  (the freebie is only marginally better than optimal); deep puzzles are
  hopeless with unguided search and should fast-fail back to sample.
- Path stitching: split sample[sid] at the midpoint, search from both
  endpoints toward center, and splice if you find a shorter bridge.
- Move cancellation: compress sample_submission paths by removing adjacent
  `X.-X` cancellations. Free 5-15% improvement with zero search.

---
name: budget_aware_per_bucket
lifecycle: active
confidence: medium
cluster: search_algorithms
supported_by: [initial_facts.md#score_anchors]
contradicted_by: []
related_ideas: [sample_submission_fallback, cayleypy_beam_search, predictor_training]
---

# Budget-aware per-bucket search

The score is dominated by the `very_hard` bucket (ids 501-1000, or ids
{500, 510, ..., 1000} in the stratified proxy — 50 out of 101 puzzles).
Spending equal wall-clock on every puzzle is wrong:

- `short` (depth 1-25): cheap; beam_width ~256, max_steps = 2×depth.
  Should solve all with compression_ratio ≈ 0.3-0.5 easily.
- `medium` (depth 26-100): unguided beam's sweet spot. beam_width ~1024,
  max_steps = depth + 20.
- `hard` (depth 101-500): unguided beam fails. Either use a trained
  predictor, MITM, or bail quickly to sample_submission.
- `very_hard` (depth 501-1000): no single-pass search works. Consider
  preprocessing (macro-move compression of sample) + partial search, or
  falling back entirely.

Strategic question: is it better to spend 5 minutes solving one `very_hard`
puzzle 50% shorter (saves ~250 moves), or 30 seconds per puzzle on 10
`short` puzzles solving each 80% shorter (saves ~10 moves each = 100 total)?
The first wins. Prioritize depth over breadth in budget allocation.

The `.score` sidecar's `bucket_<name>_fitness` / `bucket_<name>_solved`
tell you exactly where the leverage is after each eval.

---
name: cayleypy_beam_search
lifecycle: active
confidence: high
cluster: search_algorithms
supported_by: [baseline_cayleypy.py]
contradicted_by: []
related_ideas: [predictor_training, meet_in_the_middle, sample_submission_fallback]
---

# CayleyPy beam search (no predictor)

Use `helpers.core.cayleypy_beam_solver(state, beam_width=W, max_steps=S)` to
solve one state. Beam width 1000 + 200 steps typically solves shallow
scrambles; fails on deep ones. Tradeoffs:

- Wider beam = better quality, more memory + time.
- Larger max_steps = solves deeper scrambles but eats budget.
- Tune per-puzzle: cheap budget for likely-easy ones, expensive for hard ones.

Watch out: cayleypy returns generator INDICES, not Kaggle move names.
`cayleypy_beam_solver` already handles the translation.

---
name: predictor_training
lifecycle: active
confidence: medium
cluster: machine_learning
supported_by: []
contradicted_by: []
related_ideas: [random_walk_data, cayleypy_beam_search]
---

# Train a custom Megaminx predictor

cayleypy has no pretrained predictor for Megaminx. Generate (state,
distance-to-solved) pairs by random walks from the central state, train a
small MLP to predict distance, plug into beam search. Top Kaggle entrants did
exactly this. cayleypy exposes `RandomWalksGenerator` and a `Predictor` class
to plug into `BeamSearchAlgorithm.search(predictor=...)`.

---
name: meet_in_the_middle
lifecycle: active
confidence: medium
cluster: search_algorithms
supported_by: []
contradicted_by: []
related_ideas: [cayleypy_beam_search]
---

# Meet-in-the-middle (MITM)

Run BFS forward from the initial state and backward from the solved state.
When the two frontiers intersect, concatenate the half-paths. Halves the
depth requirement (depth-D problem becomes two depth-D/2 problems → memory
~24^(D/2) instead of 24^D).

cayleypy provides `MeetInTheMiddle` in `cayleypy.algo`. May be combined with
beam search: BFS one side to a fixed depth, beam-search the other.

---
name: random_walk_data
lifecycle: active
confidence: high
cluster: data_generation
supported_by: []
contradicted_by: []
related_ideas: [predictor_training]
---

# Random walks for training data

`graph.random_walks(width, length, start_state)` produces (state, distance)
pairs by walking from a known state. Use central state + many depths to
cover the distribution; train a predictor on that. Cheap to generate millions
of examples.

---
name: pattern_database_corners
lifecycle: active
confidence: low
cluster: heuristics
supported_by: []
contradicted_by: []
related_ideas: [ida_star]
---

# Pattern database: corners only

Precompute exact distance from every corner-only configuration to its solved
arrangement. With 20 corners and orientations, the corner-only state space is
small enough to enumerate. Use the precomputed distance as an admissible
heuristic for IDA* on the full puzzle. Standard Rubik's-cube technique;
adapt to Megaminx's geometry.

---
name: ida_star
lifecycle: active
confidence: medium
cluster: search_algorithms
supported_by: []
contradicted_by: []
related_ideas: [pattern_database_corners]
---

# IDA* with admissible heuristic

Iterative deepening A* with a heuristic h(state) that lower-bounds the true
distance. Memory-light (depth-first), optimality guarantees if h is
admissible. Pattern databases (corners only, edge orbits) supply h. Slower
per-state than BFS but explores far fewer states.

---
name: two_phase_kociemba_style
lifecycle: active
confidence: low
cluster: search_algorithms
supported_by: []
contradicted_by: []
related_ideas: [pattern_database_corners]
---

# Two-phase (Kociemba-style)

Reduce the problem in two stages: (1) drive the state into a smaller
sub-group (e.g. fix orientations); (2) solve within the sub-group. Each
stage uses its own pattern DB. Famous for Rubik's cube; Megaminx adaptation
needs choosing the right intermediate sub-group — non-trivial but a
research direction.

---
name: study_top_kaggle_notebooks
lifecycle: active
confidence: high
cluster: research
supported_by: [initial_facts.md]
contradicted_by: []
related_ideas: [predictor_training, meet_in_the_middle, cayleypy_beam_search]
---

# Study top Kaggle notebooks before writing solutions

`initial_facts.md` lists 6 Megaminx-specific notebooks and 6 general
cayleypy/permutation-puzzle notebooks ordered by vote count. The highest-voted
Megaminx notebook (`mitchell11/cayleypy-megaminx-base-litvinov-michael`) shows
the canonical solver structure used by competitors. The general
`fedimser/beam-search-with-cayleypy` (51 votes) is the best beam-search
tuning reference. `lilypilly/cayleypy-cube-train-and-solve-smallmodel` is the
best end-to-end "train a custom predictor and use it in beam search" template.

**Fetch a notebook locally** with:
```
set -a && source .env && set +a
kaggle kernels pull <notebook-ref> -p /tmp/nb && ls /tmp/nb
```

Look at all 6 Megaminx notebooks before committing to a search strategy.

---
name: macro_moves
lifecycle: active
confidence: medium
cluster: heuristics
supported_by: []
contradicted_by: []
related_ideas: [pattern_database_corners]
---

# Macro-move precomputation

Precompute short sequences (3-8 moves) that have clean semantics on a
specific sub-group (e.g. "rotate 3 corners around face X"). Use them as
high-level moves in a higher-level search. Reduces effective branching
factor for the high-level search at cost of longer per-step paths.
