# Debrief Report — Full Agent Gen 1

## Solutions Evaluated

| Solution | Score (mAP50) | Epochs | copy_paste | TTA | Train Time |
|----------|--------------|--------|------------|-----|-----------|
| sol01    | 0.8103       | 20     | 0.5        | Yes | 240.5s    |
| sol02    | 0.8209       | 40     | 0.6        | Yes | 461.6s    |

**Best**: sol02 (mAP50 = 0.8209)

## What I Tried

1. **sol01**: Fine-tuned from WEIGHTS_EXP5 with copy_paste=0.5, label_smoothing=0.05, TTA — baseline 0.8103
2. **sol02**: Fine-tuned from WEIGHTS_EXP5 with copy_paste=0.6, 40 epochs, TTA — improved to 0.8209

## What Information I Lacked

- No prior generation solutions or knowledge to build on (gen 1 cold start)
- State of Affairs was empty — no strategic guidance available
- No clusters or ideas yet from previous agents

## Was the State of Affairs Accurate?

The State of Affairs accurately reflected a cold-start situation. No solutions had been evaluated yet.

## What Would I Do Differently

With more time, I would try:
- Training for the full PROXY_EPOCHS_SCRATCH=50 epochs from a COCO pretrained model to establish an independent baseline
- Experimenting with different learning rates (e.g., lr0=0.01 for fine-tuning)
- Trying the exp6 combined_aug weights (WEIGHTS_EXP6) as an alternative starting point
- Using hsv augmentation which exp6 found beneficial

## Specific Experiments to Run

1. **copy_paste sweep**: Does copy_paste=0.7 or 0.8 continue to improve? The 15x class imbalance suggests higher values may help more.
2. **WEIGHTS_EXP6 vs WEIGHTS_EXP5**: exp6_combined_aug achieved 0.936 val mAP50 — could it outperform as a fine-tuning starting point?
3. **imgsz=832**: The description mentions small lesions may benefit from larger image size.

## Helper Tools Feedback

- `train_and_eval` and `evaluate_on_test` from helpers.core worked correctly
- TTA is properly wired through `tta=True` in `train_and_eval`
- The deprecation warning on `label_smoothing` suggests removing it from future solutions
- All paths (WEIGHTS_EXP5, DATA_V1, RUN_DIR) are correct and accessible

## Time Budget

Two full evaluations completed. Ran out of time for additional iterations. Both solutions scored below the 0.92 target — more epochs or architectural changes needed.