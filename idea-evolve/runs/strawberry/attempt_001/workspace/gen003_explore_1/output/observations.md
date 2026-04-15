# Observations — gen003_explore_1

## Approach: Progressive Resizing 640→832

### What I tried
Progressive resizing: train yolo11s-seg.pt from COCO at 640 for 20 epochs (stage 1), then fine-tune at 832 for 10 epochs (stage 2), evaluate at 832.

This tests the hypothesis that direct imgsz=832 fine-tuning failed (0.5453 regression) because it destroyed domain adaptation learned at 640. By training at 640 first and then fine-tuning at 832, we may preserve domain adaptation while capturing higher-resolution disease features.

### Implementation
- Stage 1: yolo11s-seg.pt from COCO, 20 epochs, imgsz=640, lr0=0.01, copy_paste=0.5
- Stage 2: Fine-tune from stage 1's best.pt, 10 epochs, imgsz=832, lr0=0.001, copy_paste=0.5
- Fallback: If stage 2 fails, evaluate stage 1 at 640

### Status
**Could not evaluate** due to GPU contention — multiple concurrent agents (gen003_explore_2, gen003_exploit_1, gen003_full_1, EXP-6) all competing for the same GPU. The evaluation was waiting for the GPU lock when my session terminated.

### Hypothesis
Progressive resizing is fundamentally different from direct high-resolution fine-tuning because:
1. Stage 1 learns general disease features at 640
2. Stage 2 adapts to higher resolution without the catastrophic forgetting that happens when you directly switch resolution on a converged model

The key insight from gen2's failure (0.5453) was that the domain adaptation was resolution-specific. Progressive resizing sidesteps this by letting the model learn resolution-agnostic features first.

### Expected outcome
If progressive resizing works, expect mAP50 > 0.8328 (current best from direct 640 training). The 832 resolution should capture finer disease details (small lesions, early-stage symptoms).

### Alternative directions to explore
1. **Longer stage 1**: 30 epochs at 640 before moving to 832
2. **Three-stage**: 640 → 736 → 832 for smoother resolution transition
3. **Higher batch at stage 2**: batch=16 at 832 if memory allows
4. **Resolution per class**: Some diseases may benefit more from higher resolution than others