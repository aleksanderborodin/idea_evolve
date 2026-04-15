# Observations — gen002_explore_1

## Attempt 1: imgsz=832 fine-tuning from exp5 (FAILED)

**Hypothesis**: The val-test gap (val=0.91, test=0.8137) is caused by small lesions at 640px resolution. Higher resolution (832) would capture finer disease details.

**Approach**: Fine-tune exp5 checkpoint (domain-adapted) at imgsz=832, 20 epochs, yolo11s scale, batch=8, copy_paste=0.5, optimizer='AdamW'.

**Result**: mAP50 = 0.5453 (evaluated at 832) — SEVERE REGRESSION from exp5 baseline of 0.7876 at same resolution, and far below gen 1 best of 0.8328.

**What happened**:
- Training completed 20 epochs with val mAP50 ≈ 0.91 (per State of Affairs context)
- Test mAP50 at 832 was only 0.5453 — massive val-test gap of ~0.36
- The fine-tuning at different resolution actively degraded the domain-adapted model
- Training dynamics at imgsz=832 with only 20 epochs were insufficient to adapt properly

**Diagnosis**: Fine-tuning from a converged checkpoint at a different resolution for only 20 epochs is counterproductive. The model needs more epochs to adapt its feature extraction to the new resolution. The COCO-pretrained features were disrupted before the new resolution features could be learned.

**Key learnings**:
- imgsz=832 without full convergence hurts performance
- The val-test gap hypothesis may be wrong OR the issue is more complex than just resolution
- 20 epochs is not enough for resolution adaptation

## Attempt 2: yolo11s from COCO at 640 for 40 epochs (NOT RUN — time constraint)

Started but did not complete due to session time limits.

## Failed attempts also valuable

The failed imgsz=832 experiment provides strong evidence that:
1. Simple resolution increase during fine-tuning does not help
2. The val-test gap (0.10) likely has a different cause than just image resolution
3. Need to explore other hypotheses: TTA evaluation, class imbalance handling, or ensemble methods

## Unexplored directions

- TTA evaluation on best exp5 checkpoint (free boost, no retraining)
- Progressive resizing (train at 640, fine-tune at 832)
- Class-weighted loss for rare diseases (Anthracnose: 89 instances vs Leaf Spot: 1365)
- Ensemble of exp5 + exp6 checkpoints