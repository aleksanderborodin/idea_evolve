# Strawberry Disease Segmentation — Maximize mAP50

## Task

Fine-tune a YOLO11 model for **instance segmentation of 7 strawberry diseases** and maximize
the **mask mAP50 on the held-out test split** (743 images, never used during training).

**Fitness = mask mAP50 on open_v1 test split. Higher is better.**

### Disease classes (7):
0. Angular Leafspot  1. Anthracnose Fruit Rot  2. Blossom Blight  3. Gray Mold
4. Leaf Spot  5. Powdery Mildew Fruit  6. Powdery Mildew Leaf

---

## Solution format — full training script

Solutions are **Python files** where `entrypoint()` does the actual YOLO training + test
evaluation and returns a metrics dict. You have complete control over the training process.

**Minimal valid solution:**
```python
def entrypoint():
    import os, shutil
    from pathlib import Path
    os.environ["CLEARML_SDK_ENABLED"] = "0"  # prevent clearml from logging
    from ultralytics import YOLO
    from helpers.core import WEIGHTS_EXP5, DATA_V1, RUN_DIR, PROXY_EPOCHS_FINETUNE

    shutil.rmtree(RUN_DIR, ignore_errors=True)
    model = YOLO(WEIGHTS_EXP5)  # start from best known (exp5, 100-epoch trained)
    results = model.train(
        data=DATA_V1, epochs=PROXY_EPOCHS_FINETUNE,
        imgsz=640, batch=16, device=0, seed=0, deterministic=True,
        project=str(RUN_DIR.parent), name=RUN_DIR.name,
        verbose=False, plots=False,
    )
    best_pt = RUN_DIR / "weights" / "best.pt"
    eval_model = YOLO(str(best_pt))
    m = eval_model.val(data=DATA_V1, split="test", imgsz=640, device=0,
                       verbose=False, plots=False)
    shutil.rmtree(RUN_DIR, ignore_errors=True)
    mp, mr = float(m.seg.mp), float(m.seg.mr)
    return {
        "mAP50":    round(float(m.seg.map50), 4),
        "mAP50_95": round(float(m.seg.map),   4),
        "F1":       round(2*mp*mr/(mp+mr+1e-9), 4),
        "precision": round(mp, 4),
        "recall":    round(mr, 4),
    }
```

**The `entrypoint()` return dict must contain `"mAP50"` — that becomes the fitness score.**

---

## GPU lock — parallelism is handled automatically

evaluate.py holds a **system-wide GPU file lock** while training. If two agents run
`evaluate.py` at the same time, the second one blocks until the first finishes. You do not
need to worry about parallel_groups ordering — the lock makes it safe.

Each evaluation takes **~3-4 min** (20 fine-tuning epochs) or **~9 min** (50 from-scratch
epochs). Evaluate solutions one at a time — write one solution, run evaluate.py, see the
score, then decide what to try next.

---

## Two evaluation modes

### Mode 1 — Fine-tune from exp5 checkpoint (default, recommended)
Start from the best known trained model (exp5: copy_paste=0.5, 100-epoch trained, val
mAP50=0.945). Fine-tune for **20 more epochs** (`PROXY_EPOCHS_FINETUNE = 20`).

- Fast: ~3.6 min per eval
- Good proxy: model already converged, so 20 more epochs show the effect of your changes
- Fair: all solutions start from the same checkpoint

```python
from helpers.core import WEIGHTS_EXP5, PROXY_EPOCHS_FINETUNE
model = YOLO(WEIGHTS_EXP5)
model.train(..., epochs=PROXY_EPOCHS_FINETUNE, lr0=0.001, ...)
```

### Mode 2 — Train from scratch (for big architectural changes)
Start from `yolo11n-seg.pt` (pretrained COCO weights) for 50 epochs
(`PROXY_EPOCHS_SCRATCH = 50`).

- Slower: ~9 min per eval
- Needed for: different model size, radically different augmentation strategy
- Use when Mode 1 is stuck and you need to break out of the local minimum

```python
from helpers.core import WEIGHTS_BASE, PROXY_EPOCHS_SCRATCH
model = YOLO(WEIGHTS_BASE)
model.train(..., epochs=PROXY_EPOCHS_SCRATCH, lr0=0.01, ...)
```

---

## Available helpers (from helpers.core)

```python
from helpers.core import (
    # Path constants (absolute, always valid)
    WEIGHTS_EXP5,            # best.pt from exp5 (copy_paste=0.5, 100ep) — recommended start
    WEIGHTS_EXP6,            # best.pt from exp6 (combined aug, 100ep) — alternative start
    WEIGHTS_BASE,            # yolo11n-seg.pt — pretrained COCO weights, for from-scratch runs
    DATA_V1,                 # open_v1.yaml — 1450/307/743 train/val/test
    DATA_V2,                 # merged dataset yaml — adds 49 self-collected (careful: exp2 hurt)
    RUN_DIR,                 # /tmp/idea_evolve_strawberry/run — unique temp training dir

    # Epoch constants
    PROXY_EPOCHS_FINETUNE,   # 20 — fine-tuning from checkpoint (~3.6 min)
    PROXY_EPOCHS_EXTENDED,   # 40 — fine-tuning promising configs (~7.2 min)
    PROXY_EPOCHS_SCRATCH,    # 50 — from COCO base weights (~9 min)

    # Disk paths where training artifacts and per-class metrics survive cleanup
    TRAIN_LOG_DIR,           # /tmp/idea_evolve_strawberry/last_train_logs  (results.csv, args.yaml, crash_tail.log)
    LAST_PER_CLASS_METRICS,  # /tmp/idea_evolve_strawberry/last_per_class.json  (per-class mAP/P/R after last eval)

    # Utility functions
    evaluate_on_test,        # (weights_path, imgsz=640, device=0, tta=False, save_per_class=True) -> metrics dict with per_class block
    train_and_eval,          # (model_path, ..., optimizer='AdamW', lr0=0.001, tta=False, **train_kwargs) -> metrics dict
)
```

### `train_and_eval` — the "do everything" helper
Handles boilerplate: cleanup, train, log preservation, test eval, per-class metrics, optional TTA.

```python
from helpers.core import train_and_eval, WEIGHTS_EXP5

def entrypoint():
    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=20,
        lr0=0.001,
        copy_paste=0.6,      # any YOLO train() kwarg passes through
        tta=True,            # enable test-time augmentation on eval
    )
```

### `evaluate_on_test` — evaluate any checkpoint on the fixed test split
Returns `{mAP50, mAP50_95, F1, precision, recall, per_class, tta}`. The `per_class` block
has `names`, `mAP50`, `mAP50_95`, `precision`, `recall` — one entry per disease class.
Auto-writes per-class JSON to `LAST_PER_CLASS_METRICS` so you can inspect it without
re-running eval.

---

## ⚠️ REC-1: YOLO `optimizer='auto'` silently ignores your `lr0`

`train_and_eval` defaults to `optimizer='AdamW'` so your `lr0` is actually used. YOLO's
`optimizer='auto'` mode **ignores** caller-specified `lr0` / `momentum` and picks its own —
a silent footgun that compromised earlier experiments. If you call `model.train()` directly
(not via `train_and_eval`), always pass an explicit optimizer when you care about `lr0`:

```python
model.train(..., optimizer="AdamW", lr0=0.001, ...)  # lr0 respected
model.train(..., lr0=0.001)                          # lr0 SILENTLY IGNORED (auto picks)
```

---

## Agent-readable artifacts on disk (not in prompt context)

These paths persist between evaluations and survive the cleanup step. Read them via Bash
when you need detail — they are NOT in your prompt context by default.

| Path | What's there | When to read |
|------|--------------|--------------|
| `/tmp/idea_evolve_strawberry/last_train_logs/results.csv` | YOLO per-epoch losses + val mAP curves from the most recent training | Diagnose plateaus, decide if more epochs help |
| `/tmp/idea_evolve_strawberry/last_train_logs/args.yaml` | Exact config that ran (every `train()` kwarg) | Reproduce or diff your settings |
| `/tmp/idea_evolve_strawberry/last_train_logs/train.log` | Full stdout/stderr if YOLO wrote one | Debug warnings / CUDA OOM hints |
| `/tmp/idea_evolve_strawberry/last_train_logs/crash_tail.log` | Only after crash: exception + context | Root-cause a failed run |
| `/tmp/idea_evolve_strawberry/last_per_class.json` | Per-class mAP50 / mAP50_95 / precision / recall from the most recent `evaluate_on_test()` | Identify which disease is bottleneck (class imbalance is 15×) |

```bash
# Example: check if training plateaued
tail -5 /tmp/idea_evolve_strawberry/last_train_logs/results.csv

# Example: see which class is worst after your last run
cat /tmp/idea_evolve_strawberry/last_per_class.json | python3 -c \
  "import json, sys; d=json.load(sys.stdin)['per_class']; \
   print('\n'.join(f'{n}: mAP50={a:.3f} R={r:.3f}' \
   for n,a,r in zip(d['names'], d['mAP50'], d['recall'])))"
```

These artifacts are overwritten on every training run, so capture what you need before
launching the next one.

---

## What you can do that was impossible with just config settings

| Technique | Example |
|-----------|---------|
| **Staged fine-tuning** | Freeze backbone layers 0-9, train head 10 epochs, then unfreeze and train 10 more |
| **Class-weighted loss** | Upweight rare classes (Anthracnose: 89 instances vs Leaf Spot: 1365) via `cls_pw` or custom loss |
| **Progressive resolution** | Train 10 epochs at imgsz=640, then 10 at imgsz=832 for detail |
| **Larger model** | Switch to `yolo11s-seg.pt` (3.5x more params) — might capture subtler disease features |
| **Two-stage fine-tune** | Fine-tune on v2 data first (imbalanced), then fine-tune on v1 (clean) |
| **Custom augmentation pipeline** | Write albumentations transforms, patch YOLO's dataset |
| **TTA at evaluation** | Multi-scale, flipped eval to boost test mAP without retraining |
| **Ensemble** | Train two models with different seeds, average predictions on test |
| **NMS tuning** | `model.val(..., conf=0.25, iou=0.6)` — different thresholds |
| **Label smoothing** | `label_smoothing=0.1` in train() kwargs |

---

## Key findings from 8 prior experiments

| Experiment | Key change | val mAP50 (100ep) |
|-----------|------------|-------------------|
| exp8_no_aug | mosaic=0, all aug off | 0.834 — worst |
| exp4_flips | flipud=0.5, degrees=15 | 0.921 — flipud hurts |
| exp2_plus_own_data | +49 self-collected images | 0.925 — own data hurt |
| exp3_best_full | lr0=0.005 (HPO winner) | 0.929 — modest gain |
| exp7_final | aggressive multi-aug | 0.929 — too many augs |
| exp1_baseline | YOLO defaults | 0.935 — solid baseline |
| exp6_combined_aug | copy_paste=0.3 + HSV + perspective + mixup | 0.936 |
| **exp5_copy_paste** | **copy_paste=0.5** | **0.945 — best** |

**Root cause of all findings**: 15x class imbalance (Leaf Spot vs Anthracnose).
Copy-paste augmentation directly addresses this. Approaches that add noise without
targeting imbalance (flips, own data, aggressive multi-aug) hurt or show no gain.

**Convergence note**: copy_paste lags behind at epoch 20-40 but overtakes at epoch 50+.
When fine-tuning from exp5, this is already resolved — you start from the converged model.

---

## Paths for reference

```
/home/sasha/Desktop/first_project/configs/open_v1.yaml           # dataset yaml (test=743)
/home/sasha/Desktop/first_project/data/merged/dataset.yaml       # v2 merged yaml
/home/sasha/Desktop/first_project/yolo11n-seg.pt                 # COCO-pretrained base
/home/sasha/Desktop/idea_evolve/first_project/runs/segment/runs/strawberry-disease/
    exp5_copy_paste/weights/best.pt                              # WEIGHTS_EXP5
    exp6_combined_aug/weights/best.pt                            # not in weights/
/home/sasha/Desktop/idea_evolve/first_project/weights/exp6_combined_aug.pt  # WEIGHTS_EXP6
/home/sasha/Desktop/idea_evolve/first_project/configs/           # all exp YAML configs
/home/sasha/Desktop/idea_evolve/first_project/runs/segment/runs/strawberry-disease/
    exp1_baseline_open/results.csv                               # per-epoch val mAP50
    exp5_copy_paste/results.csv                                  # best experiment curves
```

Reading any `results.csv`: column 13 (0-indexed) = `metrics/mAP50(M)` (segmentation mAP50).
