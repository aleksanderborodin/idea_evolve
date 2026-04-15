# Evaluator Report — Generation 1

## Strategic Shift

**strategic_shift: false**

This generation established a baseline and identified several key patterns, but no fundamental paradigm shift occurred. The exploration revealed useful hyperparameter sweet spots and failure modes, but no new approach achieved dramatically above the proxy baseline.

## Solutions Assessed

| Solution | Score | is_valid | Central Ideas |
|----------|-------|----------|---------------|
| gen001_explore_1_sol01 | 0.0 | 0 | cls_pw class weighting (failed) |
| gen001_explore_1_sol02 | 0.8257 | 1 | copy_paste=0.7 + mosaic=0.3 |
| gen001_explore_1_sol03 | 0.8125 | 1 | copy_paste=0.8 (over-aggressive) |
| gen001_explore_1_sol04 | 0.8296 | 1 | mixup+copy_paste synergy |
| gen001_explore_1_sol05 | 0.8177 | 1 | copy_paste=0.7, mosaic=0 (harmful) |
| gen001_explore_2_sol01 | 0.0 | 0 | yolo11s from scratch (BrokenPipe) |
| gen001_full_1_sol01 | 0.8103 | 1 | baseline + TTA + label_smoothing |
| gen001_full_1_sol02 | 0.8209 | 1 | copy_paste=0.6, 40 epochs |

## What Worked

1. **copy_paste=0.7** is a clear improvement over 0.5 (baseline) and 0.8 (over-aggressive)
2. **mixup=0.15** provides complementary augmentation when combined with copy_paste
3. **Lower learning rate (lr0=0.0005)** helps stabilize training with mixup
4. **mosaic=0.3 + copy_paste=0.7** is better than either augmentation strategy alone

## What Failed

1. **cls_pw=2.0** — YOLO rejects values outside [0,1]; class weighting requires different approach
2. **TTA via augment=True** — YOLO11n-seg does not support it in val(); silently ignored
3. **yolo11s from scratch** — Training worked, but BrokenPipeError during eval cleanup (GPU lock bug)
4. **copy_paste=0.8** — Over-aggressive augmentation degraded performance

## Information Lacked

1. **Per-class mAP50 for WEIGHTS_EXP5** — We don't know how much each class improved from the 100-epoch training. Critical for targeting the bottleneck classes.
2. **YOLO11 loss computation API** — No agent successfully implemented custom loss. Research identified BCE-Dice-Lovász as promising but requires monkey-patching.
3. **Val split composition** — How many instances per class on val? Affects inverse-frequency weighting estimates.
4. **copy_paste convergence lag at 20 epochs** — The 15-epoch lag noted in description.md may affect proxy metric reliability.

## State of Affairs Accuracy

The initial State of Affairs was correctly empty (gen 0). This was a proper cold start. The description.md provided solid prior experiments (exp1-exp8) as a knowledge base, which agents used effectively.

## What Would I Do Differently

With more context, I would:
1. First run `evaluate_on_test(WEIGHTS_EXP5)` to get per-class baseline — prerequisite for targeted optimization
2. Sweep copy_paste in finer increments (0.55, 0.60, 0.65, 0.70) to find exact sweet spot
3. Test WEIGHTS_EXP6 as a starting point (0.936 val mAP50)
4. Try staged fine-tuning (freeze backbone, then unfreeze) before running full augmentation sweeps

## Specific Experiments for Generation 2

1. **copy_paste sweep (0.55, 0.65, 0.70) + mixup=0.15** — find exact optimum
2. **WEIGHTS_EXP6 vs WEIGHTS_EXP5** — is combined_aug better for fine-tuning?
3. **40 epochs on best gen1 config** (copy_paste=0.7, mixup=0.15, lr0=0.0005)
4. **Per-class baseline measurement** — run evaluate_on_test on WEIGHTS_EXP5 to get bottleneck classes
5. **Staged fine-tuning** — freeze 10 backbone layers, then unfreeze

## Surprises

1. **TTA is silently ignored** — YOLO11n-seg val() doesn't support augment=True; this was not clearly documented
2. **mixup synergy was large** — +0.004 mAP50 from just adding mixup=0.15 to copy_paste=0.7
3. **Angular Leafspot is universally weak** — Every solution scores 0.66-0.74 on this class despite different approaches
4. **yolo11s trains well** — The larger model showed no instability; BrokenPipeError is an evaluate.py bug not a model issue

## Helper Tools Feedback

- `train_and_eval` worked correctly and efficiently
- `evaluate_on_test` properly writes LAST_PER_CLASS_METRICS
- `WEIGHTS_EXP5` path is correct and accessible
- REC-1 warning about optimizer='auto' ignoring lr0 is accurate and valuable
- Missing: `get_per_class_metrics()` helper — agents must read JSON file directly

## Time Budget

Sufficient for the generation. The evaluator completed all steps (read all solutions, created knowledge files, generated reports) in adequate time. No timeout pressure experienced.