# Debrief Report — explore_2 gen001

## Solution Summary

| Solution | Approach | Score | is_valid | Notes |
|----------|----------|-------|----------|-------|
| sol01 | yolo11s-seg.pt from scratch, 50 epochs, copy_paste=0.5, lr0=0.01 | 0.0 | 0 | Training reached epoch 40, eval crashed with BrokenPipeError |

## What Was Attempted

**Track B Radical Exploration: Larger YOLO Model**

Directive was to explore yolo11s-seg.pt (small variant, 3.5x more parameters than nano) as a fundamentally different approach from the dominant yolo11n-seg.pt used in all prior experiments.

- **Model**: yolo11s-seg.pt (10M params vs nano's 2.8M)
- **Training mode**: From scratch (COCO pretrained), 50 epochs
- **Key settings**: lr0=0.01 (standard for from-scratch), copy_paste=0.5, AdamW optimizer, imgsz=640, batch=16

## Results

**sol01**: Training progressed well through 40 epochs with validation mAP50 trending from ~0.71 to ~0.81. However, the evaluation process crashed during the test evaluation phase with a BrokenPipeError in the GPU lock cleanup code. This resulted in is_valid=0 and a sentinel score of 0.

Training logs showed no signs of divergence or issues - the model was learning normally.

## Information Lacked

1. No visibility into why the GPU lock cleanup fails (BrokenPipeError suggests process communication issue)
2. Could not determine if this was a kill contract issue or a bug in evaluate.py
3. The crash logs show best.pt was saved but evaluation never completed

## Was the State of Affairs Accurate?

N/A — this was gen 1 cold start, State of Affairs was correctly empty.

## What Would I Do Differently

1. **Debug the BrokenPipeError first** — the larger model clearly trains well, but something breaks in the eval phase
2. **Use fewer epochs** — 50 epochs at yolo11s scale takes longer than expected; try 30-40 epochs
3. **Check GPU memory** — larger model may have different memory characteristics causing the eval to OOM

## Specific Experiments to Run

1. **Retry yolo11s with 30 epochs** — see if shorter training avoids the crash
2. **Check evaluate.py GPU lock code** — the BrokenPipeError is suspicious
3. **Try yolo11m-seg.pt** — even larger model (not attempted by any agent)

## Surprises

- Training was remarkably stable for a larger model — no signs of gradient explosion or instability
- The crash happened AFTER training completed successfully, during evaluation cleanup
- The larger model showed higher initial loss but was converging well

## Helper Tools Feedback

Used `train_and_eval` helper — works well for standard training loops. The helper correctly handles cleanup, checkpoint saving, and the standard train-then-eval flow.

## Time Budget

- ~20 min spent: writing sol01.py, launching eval, waiting for completion
- ~10 min waiting for crashed eval to be recognized
- The session ended before the evaluation completed, and subsequent attempts to re-run hit process conflicts