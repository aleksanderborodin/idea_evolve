---
type: idea
id: idea_011
name: "TTA is non-functional with current model weights"
lifecycle: debunked
confidence: 0.95
first_seen: gen_002
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: [sol_006]
contradicted_by: []
related_ideas: [idea_003]
cluster: cluster_002
tags: [tta, evaluation, non-functional, augmentation]
---

## What It Is

Applying Test-Time Augmentation (`augment=True` in `model.val()`) to improve evaluation metrics without retraining.

## How It Was Supposed to Work

TTA creates multiple augmented views of each test image (original, scales, flips) and averages predictions. For small lesions, multi-scale views should catch lesions at their preferred resolution. Expected improvement: 0.5-2% mAP50 boost.

## What Actually Happened

research_1 EXP-2: Applied `augment=True` to exp5 best.pt. Ultralytics printed:
"Model does not support 'augment=True', reverting to single-scale prediction"

Result: mAP50 = 0.8271 — identical to non-TTA baseline. TTA lift: +0.0000.

## Why This Happens

The exp5 checkpoint was likely exported to a format (TorchScript, ONNX, or similar) that doesn't support TTA, or Ultralytics v8.4.37 changed TTA behavior for segmentation models. When `augment=True` is passed to a model that doesn't support it, Ultralytics silently reverts to single-scale prediction with only a warning message — no error, no failure indication in the returned metrics.

## Implications

TTA cannot be used as a free-lunch evaluation improvement with current weights. The idea_003 approach of "apply TTA to best model for free boost" is fundamentally blocked. This is a hard limitation, not a parameter tuning issue.

## Path Forward

If TTA is desired, a model must be trained from scratch with TTA enabled at training time (not just evaluation time). The training process itself would need to support TTA-compatible augmentation. This is a substantially different experimental direction that has not been explored.

## Idea Status Change

idea_003 (TTA at evaluation) is debunked as an evaluation-time technique. It remains plausible as a training-time augmentation approach, but this is untested and would require significant infrastructure changes.
