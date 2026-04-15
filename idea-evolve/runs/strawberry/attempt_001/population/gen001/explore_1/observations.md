# Observations — explore gen1 explore_1

## Approaches Tried

### sol01 — cls_pw=2.0 + copy_paste=0.6
**Result: FAILED (is_valid=0)**

`cls_pw` must be in range [0, 1] in YOLO. Value 2.0 is invalid.
Lesson: cls_pw is a probability weight, not a multiplier. Not a viable approach.

### sol02 — copy_paste=0.7 + mosaic=0.3
**Result: mAP50=0.8257**

Moderate improvement from baseline 0.7 copy_paste with reduced mosaic.
Best per-class: Gray Mold (0.936), Anthracnose (0.804), Blossom Blight (0.824)
Worst: Angular Leafspot (0.708), Leaf Spot (0.756)

### sol03 — copy_paste=0.8 + tta=True
**Result: mAP50=0.8125**

Higher copy_paste actually performed worse than 0.7.
TTA was ignored ("Model does not support augment=True") for this model architecture.
Worst: Angular Leafspot (0.673), Anthracnose (0.770)

### sol04 — copy_paste=0.7 + mixup=0.15 + lr0=0.0005
**Result: mAP50=0.8296**

Best result overall. Lower learning rate + mixup combination helped.
Anthracnose improved to 0.858 (best across all solutions).
Worst: Leaf Spot (0.760), Angular Leafspot (0.744)

### sol05 — copy_paste=0.7 + mosaic=0.0
**Result: mAP50=0.8177**

Disabling mosaic entirely hurt performance vs mosaic=0.3.
Confirms that some mosaic is beneficial even with copy_paste.
Worst: Angular Leafspot (0.684), Leaf Spot (0.730)

## Key Findings

1. **cls_pw parameter is invalid above 1.0** — YOLO rejects values outside [0,1].
   Class-aware sampling requires a different mechanism (custom loss, class weights in dataset YAML).
2. **copy_paste=0.7 is better than 0.8** — diminishing returns / possible over-augmentation at 0.8.
3. **mosaic=0.3 + copy_paste=0.7** is a good combination (sol02).
4. **mixup=0.15 with copy_paste=0.7** is the best configuration found (sol04: 0.8296).
5. **Disabling mosaic hurts** — even with high copy_paste, removing mosaic degrades performance.

## Class Imbalance Observations

- Anthracnose (rarest class) improved significantly with mixup (sol04: 0.858).
- Angular Leafspot remains the most difficult class across all approaches (0.67-0.74 range).
- Blossom Blight achieves perfect recall (1.0) in most solutions — already well-represented.

## Unexplored Directions

- Staged fine-tuning (freeze backbone first, then unfreeze)
- Custom class weights via dataset YAML modification
- Larger model (yolo11s-seg.pt)
- Longer training (40 epochs instead of 20)