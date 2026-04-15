## Current Population Status
Best solution: No solutions evaluated yet (gen 1 cold start)
Second best: N/A

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/description.md` — Problem definition and key findings
- Note: exp5_copy_paste (copy_paste=0.5, 100 epochs from yolo11n-seg.pt) achieved the best val mAP50=0.945

## Directive
This is a full baseline agent. Build an end-to-end solution using the best known configuration from prior experiments.

**Task: Reproduce and slightly improve on exp5's approach as a solid baseline.**

Use the recommended fine-tuning path:
1. Start from `WEIGHTS_EXP5` (best.pt from exp5, already trained on copy_paste=0.5)
2. Fine-tune for 20 epochs with `copy_paste=0.5` (the known good value)
3. Add light test-time augmentation (TTA) at eval: `tta=True` in `train_and_eval`
4. Use lr0=0.001 (appropriate for fine-tuning)
5. Add `label_smoothing=0.05` to slightly regularize

This is the most likely to produce a reliable score. Don't get fancy — use the known winner and add one incremental improvement (TTA).

Expected runtime: ~3.6 min per eval.

Baseline to beat: exp5_copy_paste achieved val mAP50=0.945 at 100 epochs (proxy baseline ~0.92).
