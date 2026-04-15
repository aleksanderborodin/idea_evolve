# Observations — full_1, gen 1

## Approach: Strong baseline from proven best practices

Attempted to establish a solid reference by combining the two most validated findings:
- WEIGHTS_EXP5 (best checkpoint: copy_paste=0.5, 100ep, val mAP50=0.945)
- copy_paste=0.5 + lr0=0.005 (proven best settings from exp3 and exp5)

## Result

- **sol01.py** (fine-tune 20 epochs, imgsz=640, copy_paste=0.5, lr0=0.005): **mAP50 = 0.8137**
- eval_time: 244.5s (~4 min)

## Analysis

The score of 0.8137 is lower than expected. Key observations:

1. The val mAP50 at epoch 20 during training was 0.91 (on the 307 val images), but the test
   mAP50 after evaluation was 0.8137 — significant gap between val and test splits.
2. The model converged quickly (box_loss and seg_loss stabilized by epoch 5), suggesting the
   fine-tuning is mostly adjusting the head layers.
3. copy_paste=0.5 was set but the optimizer ignored lr0=0.005 and chose lr=0.000909 with AdamW
   (the "auto" optimizer mode).

## What This Tells Us

The 20-epoch fine-tune from a converged 100-epoch checkpoint shows meaningful regression on the
test split. This could be:
- The model was already overfitted to the training+val distributions at epoch 100
- The test set has different characteristics than val (different disease presentation/lighting)
- 20 epochs of fine-tuning is not enough to adapt to test distribution

## Next Directions to Explore

1. **Higher resolution (imgsz=832)** — may capture small disease lesions better on test images
2. **Longer fine-tune (40 epochs)** — PROXY_EPOCHS_EXTENDED=40, gives more adaptation time
3. **Staged fine-tune** — freeze backbone, train head 10 epochs, then unfreeze and train 10 more
4. **Class-weighted loss** — address the 15x class imbalance directly in the loss function
5. **Test-Time Augmentation (TTA)** — multi-scale and flipped inference to boost test performance
6. **yolo11s-seg** — larger model may generalize better to the held-out test set

## Time Budget

One evaluation takes ~4 minutes (20 epochs). I had time for 1-2 evaluations in this session.
The next agent (Track B) should try one of the above directions.