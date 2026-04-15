# Strawberry Problem Helpers

## core.py

Import as: `from helpers.core import WEIGHTS_EXP5, PROXY_EPOCHS_FINETUNE, PROXY_EPOCHS_EXTENDED, train_and_eval, evaluate_on_test`

### Path constants (all absolute, all verified to exist)

| Constant | Value |
|----------|-------|
| `WEIGHTS_EXP5` | exp5 best.pt (copy_paste=0.5, 100ep, val mAP50=0.945) — **recommended start** |
| `WEIGHTS_EXP6` | exp6 best.pt (combined aug, 100ep, val mAP50=0.936) |
| `WEIGHTS_BASE` | yolo11n-seg.pt (COCO pretrained, for from-scratch runs) |
| `DATA_V1` | open_v1.yaml — 1450/307/743 train/val/test |
| `DATA_V2` | merged dataset yaml — +49 self-collected images (use cautiously) |
| `RUN_DIR` | /tmp/idea_evolve_strawberry/run — temp training directory |

### Epoch constants

| Constant | Value | Use case |
|----------|-------|----------|
| `PROXY_EPOCHS_FINETUNE` | 20 | Quick exploration from exp5/exp6 checkpoint (~3.6 min) — **default** |
| `PROXY_EPOCHS_EXTENDED` | 40 | Promising configs that need more time to converge (~7.2 min) |
| `PROXY_EPOCHS_SCRATCH` | 50 | Training from COCO base weights (~9 min) |

### Functions

**`train_and_eval(model_path, data_yaml=DATA_V1, epochs=PROXY_EPOCHS_FINETUNE, ...)`**
Full training + test-evaluation in one call. Pass any YOLO train() kwargs.
Returns `{"mAP50": ..., "mAP50_95": ..., "F1": ..., "precision": ..., "recall": ...}`.

**`evaluate_on_test(weights_path, imgsz=640, device=0)`**
Evaluate any weights file on the open test split. Returns same dict as `train_and_eval`.
Useful when you have multiple checkpoints and want to pick the best one.
