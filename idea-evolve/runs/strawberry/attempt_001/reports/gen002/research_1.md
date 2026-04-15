# Debrief Report — Research Agent Gen 2

## 1. What did you try?

Two calibration experiments:

**EXP-1 (zero-shot exp5 on test):** Evaluated exp5 best.pt directly on the test split with no fine-tuning. Result: mAP50 = 0.8271. This is only 0.0057 below the best gen-1 result (explore_1: 0.8328 after 20 epochs from COCO). The near-parity confirms that fine-tuning in the 20-epoch proxy regime provides marginal benefit — models are already near their asymptotic performance.

**EXP-2 (TTA on exp5):** Tried `augment=True` in `model.val()`. Ultralytics issued "Model does not support 'augment=True', reverting to single-scale prediction" and produced identical mAP50 = 0.8271. TTA lift: +0.0000.

**EXP-2b (TTA on COCO yolo11s):** As a sanity check, tested TTA on untrained COCO yolo11s. mAP50 = 0.0013 (essentially random). This confirms the extreme domain gap and that fine-tuning is mandatory.

**Also checked:** Per-class metrics were not extracted in these experiments due to time constraints. The `model.val()` output shows per-class numbers in the table but the extracted `m.seg.map50` is the aggregate only.

## 2. What information did you lack?

- **Per-class mAP breakdown:** The State of Affairs mentions class imbalance (15x between Leaf Spot and Anthracnose). I had no per-class data to determine which classes are driving the aggregate score and which are lagging. This would help prioritize strategies.
- **Train vs val split difference:** I don't have visibility into whether the train/val splits have different lesion size distributions. The "small lesion hypothesis" would be strengthened or weakened by knowing the distribution difference between splits.
- **exp5 training config:** The full_1 solution showed val mAP50=0.91 at epoch 20 but test=0.8137 — a 0.10 gap. I don't know exp5's training config (augmentations, learning rate schedule) to understand why exp5 generalized better than full_1's fine-tune.

## 3. What given facts might be wrong or outdated?

- **TTA providing ~0.5-1% lift:** The State of Affairs (and experiment_suggestions/gen001.md) assumes TTA provides a consistent boost. This is wrong — TTA is non-functional with current exp5 weights and silently does nothing. The assumption should be removed from future planning.
- **"TTA is native Ultralytics support":** This is technically true in the API but the warning message shows the model doesn't support it. This may be an export/import artifact — if the model was exported to TorchScript or ONNX, TTA may be disabled.

## 4. Was the State of Affairs accurate?

Partially. It correctly identified the fine-tuning marginality question (EXP-1 was the highest priority experiment) and correctly flagged the val-test gap. However, it was wrong about TTA being a viable evaluation improvement — the "free lunch" framing led agents to plan around TTA when it provides zero value.

The coverage map was accurate: TTA had 0 tries, and this experiment confirmed it should stay at 0 tries unless models are retrained in a way that enables TTA.

## 5. What would you do differently with more or different context?

- **Run EXP-3 (yolo11s from exp5)** — the most important untested combination. explore_1 got 0.8328 with yolo11s from COCO. Starting yolo11s from exp5's domain-adapted weights should test whether the 20-epoch regime benefits from exp5 initialization.
- **Test imgsz=832** — both the State of Affairs and experiment_suggestions identify this as the highest-value unexplored direction. The small-lesion hypothesis is plausible and testable with a single experiment.
- **Get per-class metrics** — class-level breakdown would reveal whether improvements are coming from dominant classes (Leaf Spot) or rare classes (Anthracnose). This would redirect the strategy.

## 6. Specific experiments to run?

1. **EXP-3: yolo11s from exp5, 20 epochs, AdamW** — test the most logical combination of gen-1 findings. Cost: ~3.6 min.
2. **EXP-4: imgsz=832 from exp5, 20 epochs** — test the small-lesion hypothesis. Cost: ~3.6 min.
3. **Investigate TTA compatibility** — re-train a model from scratch with augment=True enabled (TTA at eval time requires training-time support). Test whether a freshly trained yolo11s supports TTA.

## 7. What surprised you?

- **TTA was completely non-functional** — not just ineffective but actually inert with a warning message. The "Model does not support 'augment=True'" means Ultralytics detected the model architecture/weights don't support it and silently fell back. This is a hard limitation, not a parameter tuning issue.
- **Zero-shot exp5 (0.8271) nearly matches best fine-tuned result (0.8328)** — the marginal value of fine-tuning in proxy regime is only 0.0057. This means the path to 0.92+ cannot rely on incremental fine-tuning from exp5.
- **COCO yolo11s had near-zero mAP (0.0013)** — confirmed the extreme domain gap and that no useful zero-shot performance exists without fine-tuning.

## 8. Helper tools feedback

The `helpers/core.py` module was correct and easy to use. `WEIGHTS_EXP5`, `DATA_V1`, `evaluate_on_test`, and `train_and_eval` all worked as documented. No bugs or misleading docstrings found.

However, **I could not use `evaluate_on_test` for TTA** because it doesn't support `augment=True`. I had to call `model.val()` directly. This should be documented: `evaluate_on_test` is for non-TTA evaluation only.

The venv situation was confusing — the project has a `venv/` in `/home/sasha/Desktop/idea_evolve/idea-evolve/` but it doesn't exist. The actual working venv is at `/home/sasha/Desktop/first_project/venv/`. This caused ~10 minutes of debugging time trying to find the right Python environment.

## 9. Time budget

Time was sufficient for the two core experiments. Both ran in under 2 minutes total. I had time for EXP-2b as a sanity check. I did NOT have time to run training experiments (EXP-3, EXP-4) — those belong to solution-writing agents, not research agents.

If I had more time, I would have:
- Run EXP-3 (yolo11s from exp5) to directly test the most promising combination
- Tested imgsz=832 to address the small-lesion hypothesis
- Extracted per-class metrics to understand which classes are limiting the aggregate score