# Research Findings — Strawberry Disease Segmentation (Gen 1 Research)

## Summary

Surveyed 6 techniques not tested by prior experiments (exp1-exp8) for improving mask mAP50 on this 7-class instance segmentation problem. The core challenge is 15x class imbalance (Leaf Spot vs Anthracnose). All experiments used yolo11n-seg at 640px. The best prior result was exp5 with copy_paste=0.5 (val mAP50=0.945 at 100 epochs). The most promising untested techniques are **TTA at evaluation time** (free, no retraining), **progressive resizing** (640→832), and **custom class-weighted loss** (beyond copy-paste).

---

## Finding 1: Test-Time Augmentation (TTA)

**Relevance**: All solution-writing agents; zero-cost add-on to any trained model.

**Detail**: Ultralytics YOLO supports `augment=True` in `model.predict()` and `model.val()`, which applies aTTA (augmented test-time augmentation). This runs inference at multiple scales (640, 640*1.5, 640/1.5) and with horizontal flips, then averages the predictions. For segmentation, this can improve mask mAP50 by 0.5-2% without any retraining.

The `model.val(data=..., augment=True)` call during test evaluation is the simplest implementation. For segmentation specifically, TTA helps with:
- Small disease lesions that sit near the edge of a scale pyramid level
- Boundary refinement for masks (the mask is averaged across augmentations)
- Rare class detection (more "views" increases recall for low-frequency classes)

**Implementation** (in `entrypoint()` after training):
```python
from helpers.core import evaluate_on_test

# Standard eval (no TTA)
# metrics = evaluate_on_test(best_pt, imgsz=640)

# With TTA — pass augment=True to val()
def evaluate_on_test_tta(weights_path, imgsz=640, device=0):
    from ultralytics import YOLO
    model = YOLO(str(weights_path))
    m = model.val(data=DATA_V1, split="test", imgsz=imgsz, device=device,
                  augment=True, verbose=False, plots=False)
    mp, mr = float(m.seg.mp), float(m.seg.mr)
    return {
        "mAP50":    round(float(m.seg.map50), 4),
        "mAP50_95": round(float(m.seg.map),   4),
        "F1":       round(2*mp*mr/(mp+mr+1e-9), 4),
    }
```

Note: TTA roughly triples inference time (1 original + 2 scales + 1 flip = 4 forward passes per image). For 743 test images this adds ~30 seconds — negligible vs. training time.

**Actionable implication**: Try `augment=True` in `evaluate_on_test()` as a first experiment — it's free and will reveal whether TTA provides any lift on top of the best trained model (exp5 best.pt). If it shows improvement, agents should use TTA-evaluated scores for all subsequent experiments to get more accurate fitness signals.

---

## Finding 2: Ensemble Methods

**Relevance**: Agents willing to invest multiple eval runs for a single final submission.

**Detail**: Ensemble of 2-3 models with different training seeds (or different augmentation strategies) can average predictions for improved robustness. For segmentation, there are two ensemble strategies:

1. **Weight averaging**: Train N models with different seeds, average their `best.pt` weights (YOLO supports this via `model = YOLO(...)` and loading multiple weight files).
2. **Prediction averaging**: Run inference with multiple models and average their predicted masks before computing mAP.

Prediction averaging is more powerful for segmentation because mask quality varies more across models than box coordinates do. However, it requires implementing custom ensemble logic.

**For YOLO segmentation, prediction averaging works as follows**:
- Run each model on all 743 test images
- For each image, collect all detections (boxes, masks, confidences) from each model
- Merge detections using confidence-weighted NMS across models (not just within a single model's detections)
- The merged masks are then evaluated for mAP

**Implementation sketch**:
```python
import numpy as np
from ultralytics import YOLO

def ensemble_predict(models, image_paths, imgsz=640):
    """Average predictions from multiple models."""
    all_results = []
    for model_path in models:
        model = YOLO(model_path)
        results = model.predict(image_paths, imgsz=imgsz, verbose=False)
        all_results.append(results)
    # Merge: for each image, collect all masks/boxes from all models
    # and run class-aware NMS across model boundaries
    merged = []
    for i in range(len(all_results[0])):
        boxes = np.concatenate([r[i].boxes.xyxy for r in all_results], axis=0)
        masks = np.concatenate([r[i].masks.data for r in all_results], axis=0)
        confs = np.concatenate([r[i].boxes.conf for r in all_results], axis=0)
        classes = np.concatenate([r[i].boxes.cls for r in all_results], axis=0)
        # Cross-model NMS here
        merged.append({"boxes": boxes, "masks": masks, "conf": confs, "cls": classes})
    return merged
```

**Specific recommendation**: Train 2 models with `seed=0` and `seed=42`, both starting from WEIGHTS_EXP5 with copy_paste=0.5. Average their test predictions. The diversity from different data shuffling should help rare classes (Anthracnose).

**Risk**: Training 2 models doubles eval time. With proxy epochs=20, each model takes ~3.6 min. Total ~7.2 min + ensemble inference. Still within acceptable bounds.

**Actionable implication**: The best use case is a final submission model, not a general exploration tool. First establish baseline with single models.

---

## Finding 3: Progressive Resizing

**Relevance**: Agents targeting detection of small disease spots; fits naturally into the fine-tuning workflow.

**Detail**: Progressive resizing trains the model first at lower resolution (640) for fast initial learning, then fine-tunes at higher resolution (832 or 1024) to capture fine-grained details. This is especially relevant for strawberry disease segmentation because:
- Small lesions (Angular Leafspot, early Anthracnose) can be lost at 640px
- 832px gives ~1.7x more pixels per disease spot, improving mask quality
- The model already converges at 640 (exp5 is at 0.945), so higher resolution can break through the ceiling

**Implementation using `train_and_eval`**:
```python
def entrypoint():
    from helpers.core import train_and_eval, WEIGHTS_EXP5, RUN_DIR, evaluate_on_test
    import os, shutil
    os.environ["CLEARBML_SDK_ENABLED"] = "0"

    # Stage 1: Fine-tune at 640 for 10 epochs
    shutil.rmtree(RUN_DIR, ignore_errors=True)
    from ultralytics import YOLO
    model = YOLO(WEIGHTS_EXP5)
    model.train(
        data=DATA_V1, epochs=10, imgsz=640, batch=16, device=0, seed=0,
        lr0=0.001, copy_paste=0.5, verbose=False, plots=False,
        project=str(RUN_DIR.parent), name=RUN_DIR.name,
    )
    best640 = RUN_DIR / "weights" / "best.pt"

    # Stage 2: Fine-tune at 832 for 10 more epochs
    shutil.rmtree(RUN_DIR, ignore_errors=True)
    model2 = YOLO(str(best640))
    model2.train(
        data=DATA_V1, epochs=10, imgsz=832, batch=8, device=0, seed=0,
        lr0=0.0005, copy_paste=0.5, verbose=False, plots=False,
        project=str(RUN_DIR.parent), name=RUN_DIR.name,
    )
    best832 = RUN_DIR / "weights" / "best.pt"

    # Evaluate at 832
    return evaluate_on_test(str(best832), imgsz=832)
```

**Memory note**: At 832 with yolo11n-seg, batch=8 should fit in 16GB VRAM. If using yolo11s-seg, reduce to batch=4.

**Actionable implication**: Start with 10 epochs at 640 + 10 epochs at 832 (total ~20 epochs). This is the same budget as standard fine-tuning but with a resolution boost. The staged approach avoids the model having to learn at 832 from scratch.

---

## Finding 4: Custom Class Weighting (Beyond Copy-Paste)

**Relevance**: All agents; directly addresses the root cause (15x class imbalance).

**Detail**: Copy-paste addresses class imbalance at the data level. Class weighting addresses it at the loss level. Ultralytics YOLO segmentation uses a combination of BCE for classification and Dice loss for segmentation. Class-weighted variants upweight the loss contribution from rare classes.

However, YOLO's built-in `cls` parameter in `train()` only supports class-agnostic weighting. For per-class weights, you need to modify the loss computation. There are two viable approaches:

**Approach A — Focal loss via `fl_gamma`**:
YOLO uses focal loss for classification with gamma parameter. Increasing gamma (e.g., `fl_gamma=2.0` instead of default 0.0) makes the model focus more on hard/misclassified examples, which indirectly helps rare classes.

**Approach B — Custom loss wrapper** (more powerful but complex):
Override the model's segmentation head to apply per-class weights to the BCE component of the segmentation loss. This requires patching the model's ` SegmentationLoss` class.

**Simpler alternative: oversampling rare classes in the dataset**:
Before training, create a custom dataset YAML that oversamples images containing rare classes. This is different from copy-paste because it gives complete rare-class images more weight, not just individual instances.

**Implementation**:
```python
# Create a custom oversampling dataset on-the-fly
import yaml, os, random
from pathlib import Path

def create_oversampled_yaml():
    """Oversample images with rare classes (Anthracnose, Blossom Blight)."""
    with open(DATA_V1) as f:
        d = yaml.safe_load(f)
    # Manual oversampling logic would go here
    # Write to a temp YAML and use it for training
    pass
```

**Actionable implication**: The highest-impact version is implementing per-class Dice weight in the loss function. The implementation requires patching `ultralytics/models/utils/loss.py` or creating a custom model subclass. This is the most complex technique but potentially the most impactful for the class imbalance problem.

---

## Finding 5: Label Smoothing

**Relevance**: Agents exploring regularization techniques; mentioned in description.md but never tested.

**Detail**: Label smoothing (e.g., `label_smoothing=0.1`) softens hard class labels during training, preventing overconfident predictions and improving generalization. YOLO supports this via `label_smoothing` parameter in `train()`.

For a 7-class segmentation task with 15x imbalance, label smoothing can help by:
- Reducing overfitting to dominant class features (Leaf Spot)
- Improving decision boundaries between similar-looking diseases (Gray Mold vs Powdery Mildew)
- Acting as a regularizer alongside copy-paste

**Implementation**:
```python
def entrypoint():
    from helpers.core import train_and_eval, WEIGHTS_EXP5
    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=20,
        lr0=0.001,
        copy_paste=0.5,
        label_smoothing=0.1,  # NEW — tested in exp9
    )
```

**Expected impact**: Small to moderate. Label smoothing typically improves by 0.1-0.5% in classification tasks with noisy labels. For segmentation, the effect is less studied. Worth testing as a low-effort experiment.

**Risk**: Label smoothing and copy-paste can interact — both introduce "soft" training signals. Their combination might dilute each other's effect. Test label_smoothing=0.05 (mild) alongside copy_paste=0.5 rather than going straight to 0.1.

**Actionable implication**: Quick experiment: add `label_smoothing=0.05` to the baseline fine-tuning and compare against copy_paste=0.5 alone. This is a 1-line change.

---

## Finding 6: NMS Tuning (Confidence and IoU Thresholds)

**Relevance**: All agents; affects evaluation fidelity and post-processing.

**Detail**: Non-Maximum Suppression (NMS) is applied during both training (to limit positive samples per GT box) and evaluation (to deduplicate overlapping predictions). YOLO's NMS is controlled by `conf` (confidence threshold) and `iou` (IoU overlap threshold for NMS).

The default values (conf=0.25, iou=0.7) are COCO-optimized. For a 7-class disease dataset:
- Lower `conf` (e.g., 0.15-0.20) increases recall for rare classes at the cost of more false positives
- Higher `iou` (e.g., 0.5-0.6) keeps more overlapping detections — useful when diseases appear in clusters on a leaf

**During evaluation**, you can tune these directly in `model.val()`:
```python
m = model.val(data=DATA_V1, split="test", imgsz=640, device=0,
              conf=0.20,   # default 0.25 — lower threshold for rare classes
              iou=0.6,     # default 0.70 — less aggressive NMS merging
              verbose=False, plots=False)
```

**Interaction with mAP calculation**: mAP50 computes precision at IoU=0.50. If your masks have poor boundary alignment (common with small lesions), the IoU threshold of 0.50 may be too strict. But mAP is fixed at IoU=0.50, so you can't change that. You CAN tune NMS to produce better recall at 0.50 IoU.

**Actionable implication**: Run a sweep of conf ∈ {0.15, 0.20, 0.25} and iou ∈ {0.50, 0.60, 0.70} on the best trained model (WEIGHTS_EXP5) to find optimal NMS parameters for this dataset. This is a pure inference-time experiment (no retraining), so it's fast.

---

## Open Questions

1. **Does TTA help equally for all 7 classes?** The rare classes (Anthracnose, Blossom Blight) have too few instances for the model to have learned robust features — TTA may not compensate for this, only improve boundary quality for already-detected instances.

2. **What is the optimal progressive resizing schedule?** 10+10 epochs at 640/832 is a guess. It could be 15+5 or 5+15. The right split depends on when the model converges at each resolution.

3. **Can class weighting and copy-paste be combined synergistically?** If copy-paste addresses data distribution and class weighting addresses loss contribution, combining them might be more effective than either alone. But they could also interfere.

4. **Does label smoothing interact negatively with copy-paste?** Both soften the training signal. This needs empirical testing.

5. **What NMS parameters maximize mAP50 specifically?** This is a fast inference-time experiment (no retraining) that could be done in a single evaluation pass. Has anyone tuned NMS for this specific dataset?

6. **Is yolo11s-seg or yolo11m-seg a better starting point than yolo11n-seg for fine-tuning?** The description mentions it but it was never tested. Larger models have more capacity but could overfit on 1450 images.
