## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` → mAP50 = 0.8328 (yolo11s from COCO, 20 epochs)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/full_1/sol01.py` → mAP50 = 0.8137 (yolo11n from exp5, 20 epochs)
Target: mAP50 >= 0.92

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/state_of_affairs.md` — what works, what doesn't
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/clusters/cluster_001.md` — model scale findings
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/description.md` — from-scratch training mode
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/helpers/core.py`

## This is a Track B radical exploration.
You must NOT refine the current best technique. Build a complete end-to-end solution from a different starting hypothesis.

## Directive

**Key question: Is the yolo11s at 20 epochs from COCO actually better than nano from COCO, or was it just lucky noise?**

Gen 1 explore_1 used yolo11s from COCO and got 0.8328 vs nano baseline ~0.815. But only 1 try. Run yolo11s from COCO for 50 epochs (PROXY_EPOCHS_SCRATCH) to get a proper comparison with the 100-epoch exp5 regime.

**Why this matters:** If yolo11s from COCO at 50 epochs reaches val mAP50 > 0.90, then the larger model genuinely helps and we should invest more in it. If it's still around 0.83, then the 20-epoch regime is the ceiling and we need different strategies.

**Approach:**
- Start from `WEIGHTS_BASE` (yolo11s-seg.pt, COCO pretrained) — NOT from exp5
- Use `yolo11s-seg.pt` model — the key variable (larger vs nano)
- Use `epochs=50` (`PROXY_EPOCHS_SCRATCH`) — enough to converge from scratch
- Use `imgsz=640` (standard, no resolution variable)
- Use `copy_paste=0.5` (proven best augmentation)
- Use `optimizer='AdamW'` with `lr0=0.01` (standard for from-scratch)
- Batch size: 8 (yolo11s is larger, needs more memory)

```python
from helpers.core import train_and_eval, WEIGHTS_BASE, PROXY_EPOCHS_SCRATCH

def entrypoint():
    result = train_and_eval(
        model_path=WEIGHTS_BASE,
        model_name="yolo11s-seg",
        epochs=PROXY_EPOCHS_SCRATCH,  # 50 epochs — full convergence from COCO
        lr0=0.01,                    # higher lr for from-scratch
        copy_paste=0.5,
        optimizer='AdamW',
        batch=8,
    )
    return result
```

**What to preserve:** copy_paste=0.5, AdamW optimizer.
**What to NOT revisit:** Fine-tuning from exp5 (that direction is for exploit agents), copy_paste > 0.5.
