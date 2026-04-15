# Solution-Idea Map

## Solution gen001_explore_1_sol01 (score: 0.0, INVALID)
- Central: idea_004 (cls_pw class weighting — FAILED: parameter invalid above 1.0)
- Peripheral: none
- Novel elements: Attempted cls_pw=2.0 for class imbalance — YOLO rejected with AssertionError
- Notes: cls_pw is capped at [0,1] in YOLO, not a viable class weighting mechanism

## Solution gen001_explore_1_sol02 (score: 0.8257)
- Central: idea_001 (copy_paste=0.7)
- Peripheral: idea_003 (mosaic=0.3 beneficial even with high copy_paste)
- Novel elements: First exploration of copy_paste above 0.5 in fine-tuning regime

## Solution gen001_explore_1_sol03 (score: 0.8125)
- Central: idea_001 (copy_paste=0.8 — degraded performance)
- Peripheral: idea_005 (TTA silently ignored on YOLO11n-seg)
- Novel elements: copy_paste=0.8 showed over-aggressive augmentation
- Notes: TTA was attempted but YOLO11n-seg does not support augment=True in val()

## Solution gen001_explore_1_sol04 (score: 0.8296) — BEST IN GENERATION
- Central: idea_002 (mixup+copy_paste synergy), idea_001 (copy_paste=0.7)
- Peripheral: idea_006 (lower lr0=0.0005 with mixup)
- Novel elements: First combination of mixup with copy_paste; achieved best Anthracnose mAP50 (0.858)

## Solution gen001_explore_1_sol05 (score: 0.8177)
- Central: idea_001 (copy_paste=0.7)
- Peripheral: idea_003 (mosaic=0.0 harmful even with high copy_paste — confirmed by degradation)
- Novel elements: Confirmed that completely disabling mosaic hurts performance

## Solution gen001_explore_2_sol01 (score: 0.0, INVALID)
- Central: larger_model_attempt (yolo11s-seg.pt from scratch)
- Novel elements: First attempt at yolo11s-seg.pt (larger model); training progressed well (40/50 epochs, mAP50 trending to 0.81) but eval crashed with BrokenPipeError
- Notes: GPU lock cleanup bug — not a model capacity issue

## Solution gen001_full_1_sol01 (score: 0.8103)
- Central: baseline_reproduction (exp5-style fine-tune)
- Peripheral: idea_005 (TTA attempted but not working)
- Novel elements: Confirmed TTA not working on YOLO11n; label_smoothing deprecated

## Solution gen001_full_1_sol02 (score: 0.8209)
- Central: idea_001 (copy_paste=0.6), longer_training (40 epochs)
- Peripheral: idea_005 (TTA attempted)
- Novel elements: 40 epochs from fine-tune reached 0.8209; per-class shows Angular Leafspot bottleneck (0.66)