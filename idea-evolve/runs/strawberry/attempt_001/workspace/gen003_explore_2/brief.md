## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` → mAP50 = 0.8328 (yolo11s from COCO, 20 epochs)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen002/exploit_1/sol02.py` → mAP50 = 0.8103 (yolo11n from exp5, AdamW, TTA)

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/state_of_affairs.md` — Layer 0 strategic overview
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/clusters/cluster_003.md` — Training dynamics and reliability
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/history/coverage_matrix.md` — Ideas that have been tested
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_2/sol01.py` — copy_paste=0.65 crash (FAILED)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/feedback/experiment_suggestions/gen002.md` — EXP-4: copy_paste mapping

## Directive
**This is a Track B radical exploration.** You must NOT use the current best solution as a starting point. Do NOT refine yolo11s from COCO at 640. You are mapping the copy_paste stability ceiling — a direction orthogonal to the main yolo11s trajectory.

**Primary experiment: copy_paste=0.55 and 0.6 stability mapping.**
copy_paste=0.5 is proven safe. copy_paste=0.65 crashes. The untested range (0.55-0.6) may provide better rare-class oversampling (15x Leaf Spot vs Anthracnose imbalance) without instability. Map this ceiling systematically.

**Implementation — Run TWO separate solutions:**

**sol01.py: copy_paste=0.55**
- Model: `yolo11n-seg.pt` from COCO (nano is faster, allows more iterations)
- Epochs: 20 (PROXY_EPOCHS_FINETUNE)
- copy_paste=0.55, optimizer='AdamW', lr0=0.01, batch=8, imgsz=640
- Evaluate on test split

**sol02.py: copy_paste=0.6**
- Same model, same config, copy_paste=0.6
- Evaluate on test split

**What to look for:**
- If both stable (both produce valid mAP50): ceiling is above 0.6. Test 0.62 in a follow-up run.
- If only 0.55 stable: ceiling is between 0.55 and 0.6.
- If 0.6 crashes: ceiling is below 0.6. Use 0.55 for all future copy_paste-based experiments.

**Do NOT use exp5 weights as starting point.** The nano from COCO baseline is clean for this experiment — you're measuring copy_paste stability specifically, not domain adaptation.

**Off-limits:** TTA, yolo11s from exp5, direct 832 fine-tuning.