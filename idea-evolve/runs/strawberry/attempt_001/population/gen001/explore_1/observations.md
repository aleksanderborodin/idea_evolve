# Observations — Generation 1, Explore Agent

## Approach Tried

**Track B: yolo11s-seg.pt (small model) vs yolo11n-seg.pt (nano model)**

All 8 prior experiments (exp1-exp8) used yolo11n-seg.pt (2.9M params). I explored
yolo11s-seg.pt (10.1M params) as a fundamentally different model scale — 3.5x more
parameters — never tested on this problem.

## Configuration
- Model: yolo11s-seg.pt (COCO pretrained small model, 10.1M params)
- Epochs: 20 (PROXY_EPOCHS_FINETUNE)
- Augmentation: copy_paste=0.5 (proven best from exp5)
- imgsz=640, batch=8
- Start from scratch (COCO pretrained, not from exp5 checkpoint)

## Result

| Solution | Score (mAP50) | Notes |
|----------|---------------|-------|
| sol01.py | 0.8328 | yolo11s-seg from COCO, 20 epochs, copy_paste=0.5 |

## Analysis

- **mAP50=0.8328** is lower than the nano model baseline (~0.935 at 100 epochs from exp1)
- This is expected — 20 epochs is a quick proxy, and training from COCO vs fine-tuning
  from an already-converged checkpoint are very different regimes
- The small model has 3.5x more parameters but may need more epochs to converge
- Key finding: model scale alone (s vs n) does NOT automatically give better results
  in a short fine-tuning window

## What This Means for Future Generations

- yolo11s-seg needs more than 20 epochs to show its potential — the proxy may be too short
- Fine-tuning from COCO is a weaker starting point than fine-tuning from exp5
- If exploring model scale, consider fine-tuning the small model from exp5 checkpoint
  rather than from COCO, to give it a fairer comparison
- Alternatively, try yolo11s with more epochs (40-50) to see if it catches up

## Failed Attempts

- First eval attempt got broken pipe (interrupted) — retried successfully

## Unexplored Directions

- yolo11s fine-tuned FROM exp5 checkpoint (not from COCO)
- yolo11m-seg (medium model) for comparison
- Staged training: small model with freeze backbone first, then unfreeze