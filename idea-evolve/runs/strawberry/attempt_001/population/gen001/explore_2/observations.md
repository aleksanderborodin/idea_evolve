# Observations — explore_2 gen001

## Approach Tried

**yolo11s-seg.pt from-scratch training (50 epochs)**
- Model: yolo11s-seg.pt (small, 10M params vs nano's 2.8M)
- Training: 50 epochs from COCO pretrained weights
- Settings: lr0=0.01, copy_paste=0.5, AdamW optimizer, imgsz=640, batch=16

## Results

| Solution | Score | Status |
|---------|-------|--------|
| sol01 | 0.0 (invalid) | Training completed (40/50 epochs), eval crashed with BrokenPipeError |

## What Happened

Training ran successfully and reached epoch 40 of 50 (best.pt saved at ~epoch 40), with validation mAP50 around 0.79-0.81 based on training logs. However, the evaluation process crashed during test evaluation with a BrokenPipeError in the GPU lock cleanup code. The is_valid=0 score reflects this crash.

## Key Findings

1. **yolo11s is viable for strawberry**: Training was progressing well with mAP50 trending upward (0.71 at epoch 31 → 0.81 at epoch 40). No signs of overfitting or divergence.

2. **Larger model is slower**: Each epoch took ~17-18s vs ~6-8s for nano, making 50-epoch training take longer than expected.

3. **Crash during eval**: The BrokenPipeError suggests the GPU lock cleanup code had an issue, possibly related to the kill contract or process communication.

## Why Score is 0

The entrypoint() threw a RuntimeError due to BrokenPipeError during evaluation cleanup. This made is_valid=0, resulting in a sentinel score of 0.

## Potential Next Steps (if more time)

1. Debug the BrokenPipeError in evaluate.py GPU lock code
2. Try yolo11s with fewer epochs (30 instead of 50) to fit in evaluation window
3. Use train_and_eval with TTA enabled for potential boost