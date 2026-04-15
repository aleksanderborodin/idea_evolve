## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` → mAP50 = 0.8328 (yolo11s from COCO, 20 epochs)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen002/exploit_1/sol02.py` → mAP50 = 0.8103 (yolo11n from exp5, AdamW, TTA)

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/state_of_affairs.md` — Layer 0 strategic overview
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/clusters/cluster_001.md` — Model scale and resolution exploration
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/clusters/cluster_003.md` — Training dynamics and reliability
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/history/coverage_matrix.md` — Ideas that have been tested
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/feedback/experiment_suggestions/gen002.md` — Highest priority experiments
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` — The current best (yolo11s from COCO at 20ep = 0.8328)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen002/explore_1/sol01.py` — imgsz=832 fine-tuning (FAILED: 0.5453)

## Directive
**This is a Track B radical exploration.** You must NOT use the current best solution as a starting point. Do NOT fine-tune from `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` or any exp5 weights. Start from scratch with a genuinely different approach.

**Primary experiment: Progressive resizing 640→832.**
Direct imgsz=832 fine-tuning from a 640-converged checkpoint was catastrophic (gen2 explore_1: 0.5453 regression). But progressive resizing — train at 640 for 20 epochs, then fine-tune at 832 for 10 epochs — may preserve domain adaptation while capturing higher-resolution disease features.

**Implementation:**
1. Stage 1: Train `yolo11s-seg.pt` from COCO at 640 for 20 epochs with copy_paste=0.5, optimizer='AdamW', lr0=0.01, batch=8
2. Stage 2: Load `best.pt` from stage 1, fine-tune at 832 for 10 epochs with lr0=0.001 (lower lr for fine-tuning), copy_paste=0.5, batch=8
3. Evaluate at 832 resolution

**What to preserve:** The yolo11s model architecture and the copy_paste augmentation. These have been validated.

**What to avoid:** Do NOT attempt direct 832 fine-tuning — that approach is debunked. Do NOT use exp5 or any other checkpoint as a starting point.

**Fallback if progressive resizing fails:** If stage 1 completes but stage 2 fails (OOM or regression), evaluate stage 1's best.pt at 640 to confirm the baseline still works, then document the failure mode.

**Off-limits:** TTA (debunked — non-functional), imgsz=832 direct fine-tuning (catastrophic), yolo11s+exp5 via pretrained= (architecture mismatch).