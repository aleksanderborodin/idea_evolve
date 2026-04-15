# Strawberry Helpers

> One-line index of every helper. Pick the section by the question you have
> ("how do I…"), not by name. The first paragraph of each entry tells you
> when to use it; the rest is reference.

Import path: `from helpers.core import <name>` — the solution file is run from
the workspace dir; `evaluate.py` adds the problem root to `sys.path` so this
import is the canonical form.

---

## Use this when… you want to fine-tune from a known checkpoint

**`train_and_eval(model_path, ..., **train_kwargs)`** — `helpers.core`

The 90% solution. Trains for `epochs` (default `PROXY_EPOCHS_FINETUNE=20`,
≈3.6 min on the GPU), then evaluates the best epoch on the held-out test
split. Returns `{mAP50, mAP50_95, F1, precision, recall, per_class, tta,
train_time_s}`. Pass any YOLO `model.train()` kwarg through (`copy_paste`,
`hsv_h`, `freeze`, …).

Default `optimizer="AdamW"` so your `lr0` is actually respected — YOLO's
`optimizer="auto"` silently overrides it.

```python
from helpers.core import train_and_eval, WEIGHTS_EXP5, PROXY_EPOCHS_FINETUNE

def entrypoint():
    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=PROXY_EPOCHS_FINETUNE,
        copy_paste=0.7,  # explore: more aggressive copy-paste
    )
```

## Use this when… you have a `best.pt` and just want to score it

**`evaluate_on_test(weights_path, tta=False)`** — `helpers.core`

Skips training. Useful inside an ensemble or after a custom training loop.
Set `tta=True` for YOLO's test-time augmentation (≈0.5–2% mAP50 gain, no
training cost). Writes the per-class breakdown to `LAST_PER_CLASS_METRICS`
so the next agent can `Read` it without re-running.

## Use this when… you need to reproduce a previously scored solution

**`evaluate_from_checkpoint(content_hash, run_root, tta=False)`** — `helpers.core`

When `metrics.yaml: archive_checkpoints: true`, every successful
`evaluate.py` archives `best.pt` to `<run_root>/checkpoints/<content_hash>.pt`
keyed by the solution file's content hash. This helper re-runs the test eval
against that archived checkpoint without retraining. Raises `FileNotFoundError`
if the checkpoint was LRU-evicted.

The orchestrator-facing entry point is `python3 evaluate.py --reproduce <hash>`,
which calls this internally.

## Use this when… you trained yourself and want the result archived too

**`archive_checkpoint(content_hash, run_root, src_pt=None, retention=50)`** — `helpers.core`

Normally `evaluate.py` calls this for you. Use it directly only if you ran
`model.train()` outside `train_and_eval` (e.g. multi-stage training) and want
the final `best.pt` saved alongside the score. LRU-prunes the checkpoint dir
to `retention` entries.

## Use this when… you need to read what just happened

**Disk paths (read with `Read`/`Bash`, not imported):**

| Path | Contents |
|------|----------|
| `TRAIN_LOG_DIR/results.csv` | YOLO per-epoch loss + mAP curves (last training run) |
| `TRAIN_LOG_DIR/args.yaml` | exact `train()` kwargs used |
| `TRAIN_LOG_DIR/train.log` | full stdout/stderr if YOLO emitted one |
| `TRAIN_LOG_DIR/crash_tail.log` | only on crash — exception + run dir |
| `TRAIN_LOG_DIR/best.pt` | the best checkpoint (cleared between runs) |
| `LAST_PER_CLASS_METRICS` | JSON: `{names, mAP50, mAP50_95, precision, recall}` per class |
| `<solution>_crash_logs/` | snapshot of `TRAIN_LOG_DIR` if THIS solution crashed (per-solution copy, not overwritten) |

`TRAIN_LOG_DIR = /tmp/idea_evolve_strawberry/last_train_logs`
`LAST_PER_CLASS_METRICS = /tmp/idea_evolve_strawberry/last_per_class.json`

## Reference: constants

| Constant | Value | Use |
|----------|-------|-----|
| `WEIGHTS_EXP5` | exp5 best.pt (val mAP50=0.945) | **recommended start point** |
| `WEIGHTS_EXP6` | exp6 best.pt (val mAP50=0.936) | alternative start |
| `WEIGHTS_BASE` | yolo11n-seg.pt (COCO pretrained) | from-scratch runs |
| `DATA_V1` | open_v1.yaml — 1450/307/743 | default dataset |
| `DATA_V2` | merged dataset yaml — +49 self-collected | use cautiously |
| `RUN_DIR` | /tmp/idea_evolve_strawberry/run | temp train output |
| `PROXY_EPOCHS_FINETUNE` | 20 | quick fine-tune (~3.6 min) — default |
| `PROXY_EPOCHS_EXTENDED` | 40 | promising configs (~7.2 min) |
| `PROXY_EPOCHS_SCRATCH` | 50 | from-scratch (~9 min) |
| `DATASET_STATS` | dict with class names, counts, imbalance | reference |
| `EXPERIMENT_RESULTS` | dict of prior 100-epoch val mAP50 by experiment | sanity-check |
