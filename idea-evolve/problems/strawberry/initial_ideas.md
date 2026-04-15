# Initial Ideas — Strawberry Disease Segmentation

## 1. Copy-paste augmentation for class imbalance

Copy-paste augmentation (`copy_paste=0.5`) was the single most effective improvement found.
The dataset has a ~15x class imbalance (Leaf Spot: ~1365 instances vs Anthracnose: ~89).
Copy-paste pastes segmented disease instances from one image onto another, oversampling rare
classes in varied scenes. This is the Ultralytics-native approach to class balancing for
instance segmentation.

Key observation: copy_paste converges SLOWER than baseline at epoch 20-40 but overtakes
it at epoch 50+ (reaches 0.945 vs 0.935 at 100 epochs). Do not be fooled by early epochs.

**Direction**: increase `copy_paste` probability, try `copy_paste_mode="mixup"` vs `"flip"`.

## 2. Augmentation can hurt if overdone

Combining multiple augmentations (exp6, exp7) produced WORSE results than using copy_paste
alone (exp5). Too many augmentations dilute the class-balancing signal and may introduce
distributions the model hasn't seen in the original dataset.

**Direction**: test individual augmentations independently before combining them.

## 3. Self-collected data hurt performance

Adding 49 self-collected annotated images (exp2, dataset v2) made performance WORSE than
using only the open dataset (exp1). Likely cause: the self-collected images had lower-quality
annotations (SAM2 auto-label with limited manual review) and only covered 5 of 7 classes.

**Direction**: be cautious with `dataset: "v2"`. May help if annotation quality improved.
Consider weighting self-collected images lower or using them only for specific classes.

## 4. Vertical flips hurt performance

Adding `flipud=0.5` (exp4) hurt mAP50 vs baseline. Hypothesis: disease appearances on leaves
may have a consistent orientation (top/bottom of leaf is meaningful), so vertical flips create
unrealistic training examples.

**Direction**: keep `flipud=0.0` or use very low probability (< 0.1).

## 5. Larger model architecture

All experiments used `yolo11n-seg.pt` (2.9M parameters). Upgrading to `yolo11s-seg.pt`
(10.1M) or `yolo11m-seg.pt` (22.4M) could improve capacity to model subtle disease features.
The RTX 5060 Ti has 16 GB VRAM — yolo11s runs fine at batch=16, yolo11m at batch=8.

**Direction**: evaluate `yolo11s-seg.pt` as a drop-in replacement. Test if the capacity
gain justifies the 3x slower training.

## 6. Learning rate tuning

HPO grid (exp3) found that `lr0=0.005` worked slightly better than the default `lr0=0.01`
for this dataset. The improvement was modest (0.929 vs 0.935 for baseline).

**Direction**: lr0 in range [0.003, 0.01] appears optimal. The cosine LR schedule with
`lrf=0.01` may benefit from tuning `lrf` independently.

## 7. Higher resolution inputs

Training at `imgsz=832` or `imgsz=1024` could help detect small disease spots that are
currently lost at 640px resolution. Disease lesions can be very small relative to the leaf area.

**Direction**: test `imgsz=832` with batch=8 (to fit GPU memory). May need longer warmup.
