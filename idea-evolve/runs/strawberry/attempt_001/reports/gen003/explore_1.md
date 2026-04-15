# Debrief Report — gen003_explore_1

## 1. What did you try?

**Progressive resizing 640→832** with yolo11s from COCO:
- Stage 1: Train yolo11s-seg.pt from COCO at 640 for 20 epochs (lr0=0.01, copy_paste=0.5)
- Stage 2: Fine-tune from stage 1's best.pt at 832 for 10 epochs (lr0=0.001, copy_paste=0.5)
- Evaluate at 832 on test split

This approach tests whether progressive resizing can capture higher-resolution disease features without destroying domain adaptation, which direct 832 fine-tuning catastrophically failed to do (0.5453 regression in gen2).

**Result: Could not evaluate** — GPU was occupied by concurrent agents (gen003_explore_2, gen003_exploit_1, gen003_full_1, EXP-6). Evaluation was waiting for GPU lock when session terminated.

## 2. What information did you lack?

- **Real-time GPU queue visibility**: I had no way to see how many jobs were queued or estimated wait times. This is a known gap (DESIGN-14, DESIGN-15).
- **Whether progressive resizing has any prior art in this codebase**: No experiments in `experiments/` directory tested this specific approach.
- **Per-class performance data from prior runs**: The last_per_class.json showed aggregate metrics but I couldn't correlate with specific experiments.

## 3. What given facts might be wrong or outdated?

The State of Affairs correctly identifies progressive resizing as the top untested experiment. The coverage matrix shows idea_006 (progressive resizing) with 0 trials, which is accurate.

The gen2 failure (0.5453 at imgsz=832) is correctly attributed to "domain adaptation is resolution-specific and is wiped by 20 epochs at a new resolution." Progressive resizing directly addresses this hypothesis.

## 4. Was the State of Affairs accurate?

Yes. The State of Affairs was accurate and well-structured:
- Best score correctly identified as 0.8328 (gen001 explore_1)
- Progressive resizing correctly prioritized as #2 highest-priority untested experiment
- The analysis of why imgsz=832 failed is correct

## 5. What would you do differently with more or different context?

- **Check GPU queue before starting**: If I'd known other agents were queued, I might have waited or chosen a different approach
- **Shorter training budget**: Stage 1 at 15 epochs + Stage 2 at 5 epochs would have been faster to evaluate
- **Run stage 1 only first**: Test if stage 1 alone (yolo11s at 640, 20 epochs) matches the known 0.8328 before investing in stage 2

## 6. Specific experiments to run

1. **Progressive resizing 640→832** (this attempt): Does higher resolution capture finer disease features?
2. **Progressive resizing 640→832 with TTA**: Even if progressive resizing matches baseline, TTA at 832 might provide additional lift
3. **Longer stage 1 (30 epochs at 640)**: More training at 640 before moving to 832
4. **Per-class resolution sensitivity**: Which diseases benefit most from higher resolution?

## 7. What surprised you?

The GPU contention was more severe than expected. Multiple agents in the same generation all trying to run 20-epoch YOLO trainings simultaneously is not sustainable. The system needs better evaluation queue management (DESIGN-14, DESIGN-15).

## 8. Helper tools feedback

Used `train_and_eval` and `evaluate_on_test` from `helpers.core` — both worked as documented. The fallback pattern (try stage 2, fall back to stage 1 evaluation) is sound.

The `PROXY_EPOCHS_FINETUNE`, `WEIGHTS_BASE`, and other constants in `helpers.core` were correct and useful.

## 9. Time budget

**Insufficient time**: GPU contention prevented evaluation. The solution code is correct and complete, but the evaluation never ran.

With more time, I would:
1. Wait for GPU availability and re-run the evaluation
2. If still blocked, try a shorter training budget (15+5 instead of 20+10)
3. Try a simpler variant: just stage 1 (yolo11s at 640, 20 epochs) which should match the known 0.8328 baseline

## Technical notes

The solution uses `train_and_eval` helper which correctly:
- Handles cleanup between stages
- Preserves training logs to `TRAIN_LOG_DIR`
- Returns proper metrics dict with mAP50, mAP50_95, F1, precision, recall

The fallback mechanism (if stage 2 fails, evaluate stage 1 at 640) is a good robustness feature that ensures at least some score is returned.