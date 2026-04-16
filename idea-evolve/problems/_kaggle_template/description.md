# <PROBLEM_TITLE>

Kaggle competition: `<KAGGLE_COMP_ID>` — <CLASSIFICATION: A | B | C | D>.

## Task

<One-paragraph description of the problem. What goes in, what comes out, how
Kaggle scores it. Include direction (higher/lower is better) and a link to the
competition overview.>

## Score

Primary metric: `<METRIC_NAME>` — `<higher_is_better | lower_is_better>`.
Local evaluation uses <self_check | holdout split | simulator>; see
`docs/problem_design_guide.md` §13 for what each strategy means.

Current leaderboard top: `<SCORE>`. Greedy/baseline: `<SCORE>`. Target: `<SCORE>`.

## Solution format

```python
# solution.py

def entrypoint():
    from helpers.core import load_test, score_predictions  # etc.
    # build <PREDICTIONS> from loaded test data
    return predictions  # dict[<input_id>, <output_shape>]
```

The returned dict shape is problem-specific. `evaluate.py` translates
predictions → metric score via `helpers.core.score_predictions()`.

## Local evaluation

- Test data: `data/<TEST_FILE>` — <N> items.
- Proxy subset: `data/<TEST_FILE>` first `PROXY_SIZE` items (see `helpers/core.py`).
- Full eval: operator-only via `python3 evaluate.py --full <solution.py>`.
- Sentinel: invalid output → `fitness = <SENTINEL_VALUE>`, `is_valid = 0`.

## Reproducing a scored solution

<If class A/B: cache-hash IS reproduction — identical bytes produce identical
score. No re-run needed.>

<If class C: document the holdout seed + how to re-score top solutions on the
real leaderboard via `scripts/submit_to_kaggle.py`.>

## Available helpers

See `helpers/README.md`. Key symbols:

- `DATA_DIR` — absolute path to `problems/<id>/data/`.
- `PROXY_SIZE` / `FULL_SIZE` — subset-vs-full test counts.
- `load_test(proxy: bool)` — returns test rows as a dict keyed by input id.
- `score_predictions(predictions)` — returns `(fitness, is_valid, aux_metrics)`.

## Disk artifacts

- `data/<TEST_FILE>` — Kaggle test inputs.
- `data/<SAMPLE_SUBMISSION_FILE>` — Kaggle format reference.
- `data/.kaggle_spec.yaml` — committed classification manifest.
