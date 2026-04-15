## Current Population Status
Best solution: No solutions evaluated yet (gen 1 cold start)
Second best: N/A

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/description.md` — Problem definition and key findings
- Note: Prior experiments all used yolo11n-seg.pt (nano, smallest model). No one has tested a larger model.

## Directive
This is a Track B radical exploration. You must NOT use the current dominant technique as your starting point.

**Task: Explore a larger YOLO model variant (yolo11s-seg.pt — small, 3.5x more parameters than nano).**

All prior experiments (exp1-exp8) used yolo11n-seg.pt (nano). The disease features are subtle (especially early-stage Anthracnose fruit rot). A larger model might capture finer segmentation boundaries.

Key considerations:
1. Use `WEIGHTS_BASE` (yolo11n-seg.pt) is NOT the right start — you want `yolo11s-seg.pt`. Load it directly: `from ultralytics import YOLO; model = YOLO("yolo11s-seg.pt")`
2. Train for 50 epochs from scratch (PROXY_EPOCHS_SCRATCH=50, ~9 min) — fine-tuning a large model from a nano checkpoint doesn't make sense
3. Keep augmentation moderate: copy_paste=0.5 since that was proven effective
4. Use lr0=0.01 (standard for from-scratch training, not the 0.001 fine-tune lr)
5. Larger model + more epochs = longer runtime, so this takes ~9 min per eval

Do NOT fine-tune from exp5. Start fresh with pretrained COCO weights.

Baseline to beat: exp5_copy_paste achieved val mAP50=0.945 at 100 epochs (proxy baseline ~0.92).
