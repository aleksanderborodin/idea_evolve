# Helpers — <PROBLEM_TITLE>

One-line index of every symbol agents may import from `helpers.core`.

## Constants

| Name | Value | Use when |
|---|---|---|
| `DATA_DIR` | `Path` | You need the absolute path to competition data files. |
| `PROXY_SIZE` | `int` | Sizing the iteration-fast test subset (see §13.9). |
| `FULL_SIZE` | `int \| None` | Sizing the full test set for periodic re-scoring. |
| `DEFAULT_MODE` | `"proxy"` | Default mode when a solution doesn't specify. |
| `SENTINEL_ROW_SCORE` | `int` | Contribution of a single invalid row to fitness. |

## Functions

| Name | Signature | Returns |
|---|---|---|
| `load_test` | `(proxy: bool = True) -> dict` | Test rows keyed by input_id. |
| `score_predictions` | `(predictions) -> (fitness, is_valid, aux)` | Score + validity + auxiliaries. |

## Artifacts

| Path | Contents |
|---|---|
| `data/<TEST_FILE>` | Kaggle test inputs. |
| `data/<SAMPLE_SUBMISSION_FILE>` | Kaggle submission format reference. |
| `data/.kaggle_spec.yaml` | Committed classification manifest. |
