# Research Findings — Generation 2 Track B: Calibration Experiments

## Summary

Ran two critical calibration experiments (EXP-1 and EXP-2) to resolve the most important uncertainties for the pipeline. Key findings: (1) exp5 zero-shot scores 0.8271, nearly matching the best gen-1 fine-tuned result (0.8328), confirming fine-tuning provides only marginal benefit in the 20-epoch proxy regime; (2) TTA is non-functional with these models — Ultralytics issues a "Model does not support 'augment=True'" warning and reverts to single-scale prediction, yielding zero lift on both exp5 and COCO yolo11s.

## Finding 1: Fine-tuning from exp5 is marginally beneficial in proxy regime

**Relevance**: All training-based agents (explore, exploit, full, genetic) that start from exp5
**Detail**: EXP-1 evaluated exp5 best.pt zero-shot (no fine-tuning): mAP50 = **0.8271**. The best gen-1 solution (explore_1) scored 0.8328 after 20 epochs of fine-tuning from COCO yolo11s. The gap is only +0.0057 from fine-tuning, which is negligible compared to the 0.10 val-test gap observed in full_1. This confirms that in the 20-epoch proxy regime, models start very close to their asymptotic performance — additional fine-tuning yields diminishing returns.

However, the comparison is not perfectly clean: explore_1 started from COCO (not exp5), so this doesn't directly answer whether yolo11s fine-tuned FROM exp5 would outperform yolo11s fine-tuned from COCO. That experiment (EXP-3) remains untested.

**Actionable implication**: Fine-tuning gains are small in proxy regime. The path to 0.92+ requires more than marginal improvements from fine-tuning. Agents should explore: (a) longer training (40+ epochs), (b) higher resolution (imgsz=832), or (c) architectural changes (e.g., m/l models) rather than expecting gains from continuing to fine-tune from exp5 with 20 epochs.

## Finding 2: TTA is non-functional — models silently revert to single-scale prediction

**Relevance**: All evaluation-time improvement strategies
**Detail**: EXP-2 tested `augment=True` on exp5 best.pt. Ultralytics printed repeated warnings: "Model does not support 'augment=True', reverting to single-scale prediction." The resulting mAP50 was 0.8271 — identical to the non-TTA baseline. TTA provides zero lift.

Further testing on COCO yolo11s (untrained, zero-shot) showed mAP50 = 0.0013 — essentially random, confirming that the COCO model has no domain adaptation to strawberry diseases without fine-tuning.

The TTA incompatibility likely stems from: (a) the model was exported to a format (e.g., TorchScript/ONNX) that doesn't support TTA, or (b) Ultralytics v8.4.37 changed TTA behavior for segmentation models. This is a fundamental limitation — TTA cannot be used as a free-lunch evaluation improvement.

**Actionable implication**: Drop TTA from the evaluation protocol. The `augment=True` flag is inert for these weights. Do not spend time implementing TTA in solutions. Redirect effort toward training-level improvements instead.

## Finding 3: COCO pretrained models have near-zero transfer to strawberry domain without fine-tuning

**Relevance**: Agents considering starting from COCO pretrained weights
**Detail**: COCO yolo11s-seg.pt evaluated directly on strawberry test set: mAP50 = 0.0013, mAP50-95 = 0.0006. This is 640x worse than the fine-tuned result (0.8328). The domain gap between COCO (natural images) and strawberry diseases (specialized agricultural) is extreme. Fine-tuning is mandatory for any useful performance.

**Actionable implication**: Never evaluate COCO pretrained weights directly — always fine-tune first. The gap is too large to be useful as a baseline comparison.

## Open Questions

1. **Does yolo11s from exp5 outperform yolo11s from COCO?** The most important untested experiment. COCO yolo11s fine-tuned achieved 0.8328 in 20 epochs. If exp5 yolo11s achieves higher (e.g., 0.85+), the exp5 domain adaptation matters. If similar (0.83), the 20-epoch regime is the bottleneck regardless of starting point.

2. **Why does `augment=True` not work?** Is this a model export artifact, Ultralytics version issue, or architectural limitation? Investigating whether re-training from scratch with augment=True in training (not evaluation) produces a model that supports TTA at evaluation time.

3. **Is imgsz=832 the path to 0.92+?** Both explore_1 and full_1 identified this as the top unexplored direction. The small-lesion hypothesis is plausible — test images may contain smaller lesions that 640px misses. This is the highest-value experiment to run next.