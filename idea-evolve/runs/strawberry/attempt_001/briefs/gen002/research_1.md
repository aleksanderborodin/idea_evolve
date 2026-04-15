## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` → mAP50 = 0.8328 (yolo11s from COCO, 20 epochs)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/full_1/sol01.py` → mAP50 = 0.8137 (yolo11n from exp5, 20 epochs, optimizer bug)
Target: mAP50 >= 0.92

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/state_of_affairs.md` — current knowledge state
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/clusters/cluster_002.md` — evaluation-time techniques (TTA, zero-shot)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/feedback/experiment_suggestions/gen001.md` — ranked experiments, EXP-1 and EXP-2 are highest priority
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/helpers/core.py` — evaluate_on_test function

## This is a Track B research mission.
Find approaches the system has never tried. Read the coverage matrix and dead ends list to know what has been tried. Look for ideas from adjacent fields, recent papers, or mathematical theory that could apply.

## Directive

Run TWO critical calibration experiments. These take ~30-60 seconds total and resolve the most important uncertainties for the entire pipeline:

**Experiment 1 — EXP-1: Zero-shot baseline for exp5 best.pt on test (HIGHEST PRIORITY)**
- Hypothesis: Fine-tuning from exp5 for 20 epochs is neutral or harmful compared to zero-shot. full_1 scored 0.8137 — same as gen-0 baseline that started from COCO. If exp5 already scores 0.8137 zero-shot, fine-tuning provides zero benefit.
- Method: Call `evaluate_on_test(WEIGHTS_EXP5)` — NO training, pure inference, ~30 seconds
- Deliverable: Record the zero-shot mAP50. Report whether it equals 0.8137 (fine-tuning useless), is lower (fine-tuning helpful), or is higher (exp5 generalizes well).

**Experiment 2 — EXP-2: TTA on best gen_1 model**
- Hypothesis: Test-Time Augmentation provides a consistent ~0.5-1% mAP50 lift at zero training cost.
- Method: Evaluate `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` with `augment=True` in `model.val()`. Use `evaluate_on_test()` as a template but pass `augment=True`.
- Deliverable: Compare TTA mAP50 vs non-TTA baseline of 0.8328.

**Important implementation note:** `evaluate_on_test()` does NOT currently support `augment=True`. You must implement TTA manually:
```python
from ultralytics import YOLO
from helpers.core import DATA_V1
model = YOLO("/path/to/weights.pt")
m = model.val(data=DATA_V1, split="test", imgsz=640, device=0, augment=True, verbose=False, plots=False)
# extract m.seg.map50, m.seg.map, m.seg.mp, m.seg.mr
```

Also look for any other quick-win evaluation improvements (NMS threshold tuning, different conf values) mentioned in research_1's gen 1 report.

Produce a findings report summarizing both experiments with concrete numbers. This is NOT a solution-writing task — you produce a `report.md` with experimental results.
