# Megaminx — solve 1001 scrambled states optimally

Kaggle competition: [`cayley-py-megaminx`](https://www.kaggle.com/competitions/cayley-py-megaminx)
(Class A — see [docs/problem_design_guide.md §13](../../../docs/problem_design_guide.md)).
Local score = Kaggle score (self-checking metric).

## Task

Given 1001 scrambled Megaminx states (length-120 permutations), produce a
sequence of moves that returns each state to the solved (central) state.
Score = sum of path lengths over all puzzles. **Lower is better.**

- Top Kaggle leaderboard: **80,499** (~80 moves/puzzle).
- Greedy/baseline tier: ~413k–500k.
- Target: **90,000** (≈ top-10).

## Puzzle representation

A Megaminx state is a tuple of 120 ints, each in `0..119`. The solved state
is `(0, 1, 2, ..., 119)`. A move is a named permutation; applying a move to
state `s` produces `s' = (s[perm[0]], s[perm[1]], ..., s[perm[119]])`.

24 generators: `U, -U, D, -D, F, -F, B, -B, L, -L, R, -R, DR, -DR, DL, -DL,
FR, -FR, FL, -FL, BR, -BR, BL, -BL`. `-X` is the inverse of `X`. The
authoritative list is `helpers.core.GENERATOR_NAMES`.

A path is a dot-joined string of move names: `"U.F.-R.DL"`. Empty string =
no moves.

## Solution format

```python
def entrypoint() -> dict[int, str]:
    from helpers.core import load_test, cayleypy_beam_solver
    tests = load_test(proxy=True)
    return {
        sid: (cayleypy_beam_solver(state, beam_width=512, max_steps=80) or "")
        for sid, state in tests.items()
    }
```

`entrypoint()` returns `{initial_state_id: dot_joined_path}`. Missing keys
or paths that don't actually solve the puzzle contribute the per-row sentinel
(1,000,000) to fitness; one bad row drops `is_valid` to 0 and adds 1e6 to
the total.

## Local evaluation

`evaluate.py` does:

1. AST validate that `entrypoint` exists.
2. SHA-256 the solution file → cache lookup. Same bytes = same score
   (instant return).
3. Call `entrypoint()` → get `{sid: path}`.
4. For each test puzzle: validate every move name; apply path; check final
   state == solved. Score the row.
5. Sum per-row scores → primary fitness. Aux metrics:
   `avg_path_length, solved_count, expected_count, invalid_count`.

```
python3 evaluate.py path/to/solution.py            # default: proxy 100 puzzles
python3 evaluate.py --full path/to/solution.py     # operator-only: full 1001
```

## Proxy vs full

- Proxy (`load_test(proxy=True)`): first 100 puzzles by id ASC.
  ~30 s with `baseline_cayleypy` (beam_width=512, max_steps=80).
- Full (`load_test(proxy=False)`): all 1001 puzzles.
  ~5 min with the same baseline; what Kaggle actually scores.

The solution itself picks the mode by passing `proxy=True/False` to
`load_test`. `evaluate.py` exposes `--full` as an operator override (the
cache key incorporates the mode so proxy and full results don't collide).
This matches strawberry's Mode 1 vs Mode 2 pattern; see §13.9 of the design
guide for why the solution declares the mode (cache coherence).

**Score scale.** All `metrics.yaml` numbers (`target_score`, `lower_bound`,
`upper_bound`, `significant_change`) are in **proxy units** since proxy is
the default eval mode. Approximate Kaggle full-set equivalent is `proxy ×
10.01` (linear extrapolation; calibrate against a `--full` baseline once the
distribution of difficulties on the first 100 ids is known to be skewed or
not). Top Kaggle 80,499 ≈ 8,041 proxy; user goal 78,000 Kaggle ≈ 7,800 proxy.

## Reproducing a scored solution

This problem has no stochastic training, so **the cache hash IS reproduction**.
Identical bytes → identical score, deterministically. To re-verify a
specific solution:

```
rm runs/megaminx/<attempt>/history/eval_cache.json   # or just delete the one entry
python3 evaluate.py path/to/solution.py
```

If a solution's `entrypoint()` uses non-deterministic randomness (e.g.
`random.choice` without a seed), score will drift between runs — agents must
seed RNGs explicitly.

## Available helpers

See [`helpers/README.md`](helpers/README.md). Key symbols:

- `load_puzzle_info()` — parse `data/puzzle_info.json`.
- `load_test(proxy: bool)` — return `{sid: state_tuple}`.
- `solved_state()`, `is_solved(state)`.
- `apply_move(state, name)`, `apply_path(state, path)`.
- `score_path(initial, path)` → `(length, valid)`.
- `score_predictions(predictions, proxy=True)` → `(fitness, is_valid, aux)`.
- `cayleypy_beam_solver(state, beam_width, max_steps)` — lazy-imports
  cayleypy + torch; no pretrained predictor exists, so the search is unguided.
- `GENERATOR_NAMES`, `STATE_SIZE`, `PROXY_SIZE`, `FULL_SIZE`,
  `SENTINEL_ROW_SCORE`.

## Approaches to explore

See [`initial_ideas.md`](initial_ideas.md) for the seeded ideas
(beam search, custom predictor training, meet-in-the-middle, IDA* with
pattern databases, two-phase Kociemba-style, macro-moves). The competition
top entrants used custom-trained predictors on random-walk data — that's
the highest-leverage direction.

## Hardware + concurrency

- CPU-only. `metrics.yaml: concurrency: parallel`.
- Multiple agents may evaluate solutions concurrently; no GPU lock.
- cayleypy requires torch; CPU torch is fine. Install:
  `pip install torch --index-url https://download.pytorch.org/whl/cpu` then
  `pip install cayleypy`.
- If a solution wants GPU-trained predictors, that needs DESIGN-18 (resource
  pools) to land first — see CLAUDE.md.

## Disk artifacts

| Path | Contents |
|---|---|
| `data/puzzle_info.json` | central state + 24 generators (length-120 permutations). |
| `data/test.csv` | 1001 rows: `initial_state_id, initial_state` (comma-joined permutation). |
| `data/sample_submission.csv` | Kaggle format reference. |
| `data/.kaggle_spec.yaml` | Committed classification manifest (Class A, hashes, TOS). |
| `initial_programs/baseline_random.py` | Auto-evaluated as gen 0 by the orchestrator. Cheap (~0.5 s). |
| `examples/baseline_cayleypy.py` | NOT in `initial_programs/` because beam search on 100 puzzles is ~5 min. Run manually for reference: `IDEA_EVOLVE_AGENT_NAME=manual python3 evaluate.py examples/baseline_cayleypy.py`. |

## Sentinels

- Per-row: `SENTINEL_ROW_SCORE = 1_000_000` (in `helpers.core`).
- Overall: `metrics.yaml:fitness.sentinel_value = 1_000_000_000` (1e9).
  Used when `evaluate.py` itself raises (import error, syntax error, etc.)
  rather than per-row. Filter in `orchestrator.update_rankings` is
  `score >= sentinel * 0.9` so 1e9 leaves a 3-orders buffer above any real score.
