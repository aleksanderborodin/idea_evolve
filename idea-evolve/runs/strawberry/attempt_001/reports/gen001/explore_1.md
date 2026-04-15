# Debrief Report — explore gen1 explore_1

## Solution Summary

| Solution | Configuration | mAP50 | is_valid | Key Finding |
|----------|--------------|-------|----------|-------------|
| sol01 | copy_paste=0.6, cls_pw=2.0 | 0 | 0 | cls_pw must be in [0,1] — YOLO rejects invalid values |
| sol02 | copy_paste=0.7, mosaic=0.3 | 0.8257 | 1 | Good balance of copy_paste and mosaic |
| sol03 | copy_paste=0.8, tta=True | 0.8125 | 1 | Over-augmentation with copy_paste=0.8 hurts; TTA ignored |
| sol04 | copy_paste=0.7, mixup=0.15, lr0=0.0005 | **0.8296** | 1 | Best overall; mixup + lower lr helps |
| sol05 | copy_paste=0.7, mosaic=0.0 | 0.8177 | 1 | Disabling mosaic hurts vs mosaic=0.3 |

**Best solution: sol04 with mAP50=0.8296**

## What I Tried

1. **cls_pw class weighting** — Attempted to upweight rare classes via cls_pw=2.0.
   YOLO validation failed: cls_pw must be in [0,1]. Not a viable approach.

2. **Higher copy_paste (0.6, 0.7, 0.8)** — Explored copy_paste values above the known best (0.5).
   - copy_paste=0.7 performs better than 0.8.
   - copy_paste=0.8 showed diminishing returns / degradation.

3. **Mosaic reduction (mosaic=0.3, 0.0)** — Combined with higher copy_paste.
   - mosaic=0.3 with copy_paste=0.7 works well.
   - mosaic=0.0 degrades performance — some mosaic is necessary.

4. **Mixup augmentation (mixup=0.15)** — Combined with copy_paste=0.7.
   - Best result (0.8296) — mixup provides complementary augmentation.
   - Lower learning rate (lr0=0.0005) helped stabilize training.

5. **TTA** — Tried test-time augmentation.
   - YOLO11n-seg does not support augment=True in val mode (warning logged, reverted to single-scale).
   - Not beneficial for this model.

## Information I Lacked

- The exact mechanism for class-aware sampling in YOLO (cls_pw range is [0,1], not a multiplier).
  A custom class-weight approach via the dataset YAML would be needed.
- TTA support for this specific model variant — could have been checked in docs first.

## What Surprised Me

- **copy_paste=0.8 underperformed** — Higher is not always better. The augmentation becomes
  too aggressive and may start generating unrealistic compound masks.
- **mixup + copy_paste synergize well** — The combination (sol04) beat both copy_paste alone
  and copy_paste+mosaic approaches.
- **mosaic=0 is harmful** — Even with high copy_paste, completely removing mosaic reduces
  the diversity of training samples too much.

## Helper Tools Feedback

- `train_and_eval` worked correctly and efficiently.
- `WEIGHTS_EXP5` constant was correct and valid.
- All paths from helpers.core were accurate.

## Next Steps (if continued)

1. Try copy_paste=0.65 with mixup=0.1 — fine-tune the sweet spot between 0.5 and 0.7.
2. Explore staged fine-tuning: freeze backbone 10 layers for first 10 epochs, then unfreeze.
3. Try custom class weights via modifying the dataset YAML (cls: [weight] per class).
4. Consider yolo11s-seg.pt (larger model) if compute allows.
5. Run 40 epochs (PROXY_EPOCHS_EXTENDED) on the best configuration (sol04's config).