# Debrief Report — gen002_explore_1

## 1. What did you try?

### Attempt 1: imgsz=832 fine-tuning from exp5 (PRIMARY EXPERIMENT)
- **Approach**: Fine-tune WEIGHTS_EXP5 at imgsz=832, 20 epochs, yolo11s scale, batch=8, copy_paste=0.5, optimizer='AdamW'
- **Hypothesis**: The val-test gap (val=0.91, test=0.8137) is caused by small lesions at 640px resolution. Higher resolution would capture finer disease details.
- **Result**: mAP50 = 0.5453 — SEVERE REGRESSION from gen 1 best (0.8328)
- **What happened**: Training completed with val mAP50 ≈ 0.91 but test mAP50 was only 0.5453 at 832 resolution. The val-test gap was ~0.36, far worse than the 0.10 gap seen in gen 1.
- **exp5 baseline at 832**: Evaluated exp5 directly at 832 (zero-shot) → mAP50 = 0.7876. My fine-tuned model (0.5453) was much WORSE than the original exp5 at the same resolution, confirming that fine-tuning at a different resolution for only 20 epochs actively harmed performance.

### Attempt 2: yolo11s from COCO at 640 for 40 epochs
- **Approach**: Train yolo11s-seg.pt from scratch at 640, 40 epochs, lr0=0.01, batch=8, copy_paste=0.5
- **Result**: NOT RUN — session time exceeded before evaluation could start

## 2. What information did you lack?

- Training logs/results.csv were cleaned up before I could analyze them (cleanup=True ran during timed-out evaluate.py)
- No visibility into per-epoch validation curves to understand if the model was still improving at epoch 20
- Whether the exp5 checkpoint was actually YOLO11n or YOLO11s architecture (WEIGHTS_EXP5 is 6MB which suggests nano, but the best.pt after fine-tuning was 81MB which is small)
- The original exp5 was trained at what resolution? (It was trained at 640 per standard protocol)

## 3. What given facts might be wrong or outdated?

- The State of Affairs says "yolo11s from exp5 checkpoint — combines the larger model scale with converged strawberry-domain weights" as the top priority. My experiment shows this approach actively degrades performance (0.5453 vs 0.7876 zero-shot at same resolution).
- The val-test gap hypothesis (val=0.91, test=0.8137) may not be resolution-related at all. The gap in my experiment was even larger (~0.36) when fine-tuning at a different resolution.

## 4. Was the State of Affairs accurate?

Partially. The State of Affairs correctly identified the val-test gap as a problem and suggested imgsz=832 as a direction to explore. However:
- It said "yolo11s from exp5" was the top priority, but my experiment shows this combination is counterproductive
- It didn't anticipate that fine-tuning at a different resolution would be so harmful
- The coverage map correctly shows imgsz=832 as 0 tries — now we know why: it causes regression

## 5. What would you do differently with more or different context?

- Try TTA (Test-Time Augmentation) on the exp5 checkpoint at 640 — this is a free boost with no retraining risk
- Try progressive resizing: train at 640, then fine-tune at 832 for a few epochs
- Evaluate whether the val-test gap is actually due to evaluation resolution mismatch (train at 640, eval at 832)
- Investigate class imbalance more deeply — 15x ratio between Leaf Spot and Anthracnose may be the real bottleneck
- Try ensemble of exp5 + exp6 checkpoints instead of fine-tuning

## 6. Specific experiments to run

1. **TTA on exp5**: Apply multi-scale + flip TTA to exp5 at 640. Expected: ~0.01-0.03 mAP50 boost at no training cost.
2. **Progressive resizing**: Train 20 epochs at 640, then 10 epochs at 832. May preserve domain features while adapting resolution.
3. **Class-weighted copy_paste**: Ensure rare classes (Anthracnose, Blossom Blight) are upweighted in copy_paste selection.
4. **Ensemble exp5+exp6**: Average predictions from both converged checkpoints.
5. **Zero-shot exp5 at 832**: Already tested — 0.7876. This is a strong baseline to fine-tune FROM, but fine-tuning destroyed performance.

## 7. What surprised you?

- Fine-tuning at a different resolution (832) from a converged checkpoint (exp5 at 640) was so harmful — degraded from 0.7876 to 0.5453
- The val-test gap was much WORSE after fine-tuning (0.36 vs 0.10 before), suggesting the domain adaptation was disrupted
- yolo11s from COCO at 640 for 20 epochs (gen 1 best: 0.8328) outperformed fine-tuning from domain-adapted checkpoint at 832 (0.5453) by a huge margin

## 8. Helper tools feedback

- `train_and_eval` from helpers.core works correctly
- `model_name` is NOT a valid kwarg for `train_and_eval` — must not pass it
- `PROXY_EPOCHS_SCRATCH = 50` exceeds the 20-40 epoch constraint in constraints.md
- The GPU lock works correctly — no conflicts with parallel evaluation

## 9. Time budget

- The imgsz=832 experiment used the full ~10 min timeout and timed out during evaluation
- Manual evaluation of the saved weights was needed, which consumed additional time
- Only 1 solution was fully evaluated (sol01: 0.5453)
- sol02 was written but not evaluated due to time constraints