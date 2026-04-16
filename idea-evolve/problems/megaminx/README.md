# Kaggle-competition problem skeleton

This directory is **not a runnable problem.** It is the copy-paste starting point
for new Kaggle-as-idea-evolve-problem implementations. The orchestrator skips
directories whose name starts with `_`, so this will never accidentally evaluate.

## Usage

Do **not** edit files here to make a problem. Instead:

```bash
cd idea-evolve
python3 scripts/new_kaggle_problem.py <kaggle_comp_id> <problem_id> --class A|B|C|D
```

That script copies this directory to `problems/<problem_id>/`, downloads the
competition data to `problems/<problem_id>/data/`, and writes a populated
`data/.kaggle_spec.yaml`.

## Contents

| File | Purpose |
|---|---|
| `description.md` | Agent-readable task spec with `<PLACEHOLDER>` tags |
| `metrics.yaml` | Metric specs + concurrency + archive flags |
| `evaluate.py` | CPU-parallel skeleton with cache/queue/proc_log pre-wired |
| `validate.py` | AST-level entrypoint check |
| `eval_hooks.py` | Optional failure-diagnosis hints (default kill hook) |
| `helpers/core.py` | Path constants + stub `load_test()` / `score_predictions()` |
| `helpers/README.md` | Symbol index template |
| `data/.kaggle_spec.yaml` | Committed classification manifest (placeholders) |

Follow the checklist in [docs/problem_design_guide.md §13](../../../docs/problem_design_guide.md).
