## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` → mAP50 = 0.8328 (yolo11s from COCO, 20 epochs)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/full_1/sol01.py` → mAP50 = 0.8137 (yolo11n from exp5, 20 epochs)
Target: mAP50 >= 0.92

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/state_of_affairs.md` — val-test gap is 0.10 (val=0.91, test=0.8137)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/clusters/cluster_001.md` — resolution ideas
- `/home/sasha/Desktop/idea_evolve/idea-evolve/feedback/experiment_suggestions/gen001.md` — EXP-4 is the resolution test
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` — current best
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/helpers/core.py`

## This is a Track B radical exploration.
You must NOT use the current dominant technique (fine-tuning from exp5 checkpoint). You must construct your solution from scratch using a different hypothesis.

## Directive

**Primary hypothesis: The val-test gap (val=0.91, test=0.8137) is caused by small lesions at 640px resolution.**

Test images may contain smaller or differently presented disease lesions that are poorly captured at the standard 640px input size. Higher resolution (832px) directly addresses this by providing more pixel detail per lesion.

**Approach: imgsz=832 with yolo11s from exp5**

Key constraints:
- Use `WEIGHTS_EXP5` as starting point (domain-adapted, not COCO)
- Use `yolo11s-seg.pt` for model scale (best performer at 20 epochs)
- Use `imgsz=832` (not 640) — this is the core experimental variable
- Pass `optimizer='AdamW'` EXPLICITLY (must override auto-optimizer bug)
- Use `copy_paste=0.5` (stable)
- Reduce `batch=8` to fit larger images in GPU memory
- Train 20 epochs

```python
from helpers.core import train_and_eval, WEIGHTS_EXP5, DATA_V1, PROXY_EPOCHS_FINETUNE
from ultralytics import YOLO

def entrypoint():
    # Higher resolution is the key experimental change
    result = train_and_eval(
        model_path=WEIGHTS_EXP5,
        model_name="yolo11s-seg",
        epochs=PROXY_EPOCHS_FINETUNE,
        imgsz=832,         # KEY CHANGE: 832 instead of 640
        batch=8,           # reduced for larger images
        lr0=0.001,
        copy_paste=0.5,
        optimizer='AdamW', # explicit, avoid auto-optimizer bug
    )
    return result
```

**What to look for in results:** If imgsz=832 closes the val-test gap even partially, this is the path forward. If it's neutral or worse, the small-lesion hypothesis was wrong.

**Do NOT:**
- Use copy_paste > 0.5 (unstable)
- Use yolo11n (nano — inferior at 20 epochs per gen 1 results)
- Skip the explicit optimizer='AdamW'
