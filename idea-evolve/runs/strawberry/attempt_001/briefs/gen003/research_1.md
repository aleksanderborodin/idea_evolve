## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` → mAP50 = 0.8328 (yolo11s from COCO, 20 epochs)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen002/exploit_1/sol02.py` → mAP50 = 0.8103

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/state_of_affairs.md` — Layer 0 strategic overview
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/feedback/experiment_suggestions/gen002.md` — EXP-3 (per-class mAP) and EXP-6 (TTA fresh training)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/feedback/system_recommendations.md` — REC-3: implement per-class mAP in evaluate_on_test()

## Directive
**This is a Track B research mission.** Find approaches the system has never tried. Read the coverage matrix and dead ends list to know what has been tried. Look for ideas from adjacent fields, recent papers, or mathematical theory that could apply.

**You have TWO priority experiments to run. Manage your time accordingly.**

### EXP-3: Per-class mAP50 extraction (HIGH PRIORITY — ~1 minute)
The 15x class imbalance (Leaf Spot 1365 vs Anthracnose 89) means aggregate mAP50 is dominated by the common class. No agent has per-class mAP data. This experiment eliminates guesswork.

**Run:**
```python
from helpers.core import WEIGHTS_EXP5, evaluate_on_test
result = evaluate_on_test(WEIGHTS_EXP5, save_per_class=True)
# Read per-class from LAST_PER_CLASS_METRICS
```

Extract `m.seg.cp`, `m.seg.cr`, `m.seg.ap50` per class. Map class IDs to disease names using DATA_V1. Produce a ranked list of classes by mAP50 (worst-first). Identify which classes are limiting the aggregate score.

**Deliverable:** A short findings report with:
1. Per-class mAP50 table (7 rows: disease name, mAP50, recall, precision)
2. Identification of the 2-3 bottleneck classes
3. Recommendation: should rare-class augmentation be the top priority?

### EXP-6: TTA validation after fresh training (~9 minutes)
TTA is non-functional with exp5 weights (silent revert to single-scale, zero lift). But this may be an export artifact specific to exp5. A freshly trained model might support TTA.

**Run:**
1. Train yolo11s from COCO at 20 epochs (this is a byproduct — any fresh model will do)
2. Evaluate with `augment=True` on the same model
3. Compare TTA vs non-TTA on the freshly trained model

**Deliverable:**
- TTA mAP50 vs non-TTA mAP50 on the same freshly trained model
- Whether TTA provides any lift when the model was trained in the current environment

**If TTA works on freshly trained model:** TTA direction is revived. All future evaluations should use TTA.
**If TTA still non-functional:** TTA is permanently closed in this Ultralytics version.

### Time management
EXP-3 takes ~1 minute. Run it first. Then run EXP-6 (train + eval). If time runs short, prioritize EXP-3 over EXP-6 — the per-class data is more valuable.