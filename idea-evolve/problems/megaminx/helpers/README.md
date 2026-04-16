# Helpers — Megaminx

Symbol index for `helpers.core`. Solutions import from here.

## Constants

| Name | Value | Use when |
|---|---|---|
| `DATA_DIR` | `Path` | Reading raw `puzzle_info.json`/`test.csv` directly. |
| `PUZZLE_INFO_PATH` | `Path` | The 24-generator + central-state JSON. |
| `TEST_CSV_PATH` | `Path` | The 1001 scrambled initial states. |
| `SAMPLE_SUBMISSION_PATH` | `Path` | Format reference (Kaggle's example output). |
| `STATE_SIZE` | `120` | Allocating state arrays / sanity-checking shapes. |
| `PROXY_SIZE` | `100` | Iterating fast — sized for ~30 s end-to-end on a CPU baseline. |
| `FULL_SIZE` | `1001` | Full Kaggle test set; periodic re-score only (operator `--full`). |
| `DEFAULT_MODE` | `"proxy"` | Defaults if a solution doesn't declare. |
| `SENTINEL_ROW_SCORE` | `1_000_000` | Per-row penalty for an invalid path. Overall fitness sentinel (1e9) lives in `metrics.yaml`. |
| `GENERATOR_NAMES` | `tuple[str, ...]` | The 24 Kaggle move names: `U, -U, D, -D, F, -F, B, -B, L, -L, DR, -DR, BL, -BL, FR, -FR, BR, -BR, FL, -FL, R, -R, DL, -DL`. |
| `GENERATOR_SET` | `frozenset[str]` | O(1) membership check for path validation. |

## Functions

| Name | Signature | Purpose |
|---|---|---|
| `load_puzzle_info` | `() -> dict` | Parse `puzzle_info.json`. Cached. |
| `load_test` | `(proxy: bool = True) -> dict[int, tuple]` | Test rows by sid; deterministic subset when `proxy=True`. |
| `solved_state` | `() -> tuple` | The central (solved) state. Cached. |
| `apply_move` | `(state, name) -> tuple` | One generator step; raises on unknown name. |
| `apply_path` | `(state, path) -> tuple` | Fold a dot-joined move sequence. |
| `is_solved` | `(state) -> bool` | Is this the central state? |
| `score_path` | `(initial, path) -> (length, valid)` | Length if solved, sentinel if not. |
| `score_predictions` | `({sid: path}, proxy=True) -> (fitness, is_valid, aux)` | Sum scoring with auxiliaries. |
| `write_submission` | `(predictions, path)` | Kaggle CSV format (only for `submit_to_kaggle.py`). |
| `cayleypy_beam_solver` | `(state, beam_width=1000, max_steps=200, predictor=None) -> str | None` | Lazy-imports cayleypy + torch. `predictor=None` → unguided beam. Pass a `cayleypy.Predictor` to guide the search. Slow first call. |

## Notes

- **Sign convention.** Kaggle uses `-X` for the inverse of `X`. cayleypy uses
  `M_X_inv`. The translation is internal to `cayleypy_beam_solver`.
- **No pretrained predictor.** As of cayleypy 0.1.0,
  `Predictor.pretrained(graph)` raises `KeyError` for Megaminx. The top
  Kaggle scores were achieved with custom-trained predictors or hand-tuned
  search — that's the optimization room agents have to explore.
- **Guided beam search.** `cayleypy_beam_solver(..., predictor=...)` now
  accepts any `cayleypy.Predictor`. Zero-training baseline worth trying:

  ```python
  import cayleypy
  gdef = cayleypy.Puzzles.megaminx()
  graph = cayleypy.CayleyGraph(gdef)
  predictor = cayleypy.Predictor(graph, "hamming")   # no training needed
  path = cayleypy_beam_solver(state, beam_width=512, max_steps=150,
                              predictor=predictor)
  ```

  `"hamming"` = number of cells not in their solved position. Free lower
  bound on remaining depth; often enough to break ties in the beam over
  unguided search. Train a small MLP on random-walk states for real gains.
- **Cache coherence.** `load_test(proxy=True)` deterministically returns the
  first `PROXY_SIZE` rows by sid ASC. Don't shuffle — content-hash caching
  depends on identical bytes producing identical scores.

## Disk artifacts

| Path | Contents |
|---|---|
| `data/puzzle_info.json` | 120-cell central state + 24 named generators (each a length-120 permutation). |
| `data/test.csv` | 1001 rows of `initial_state_id, initial_state` (comma-joined permutation). |
| `data/sample_submission.csv` | Kaggle format: `initial_state_id, path` (path is dot-joined move names). |
| `data/.kaggle_spec.yaml` | Committed manifest (classification, hashes, TOS-acceptance). |
