---
type: idea
id: idea_003
name: "Test-Time Augmentation (TTA)"
lifecycle: debunked
confidence: 0.0
first_seen: gen_001
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: []
contradicted_by: [sol_006]
related_ideas: [idea_011]
cluster: cluster_002
tags: [evaluation, inference, non-functional]
---

## What It Is

Apply augmented test-time evaluation (multi-scale + horizontal flips) when computing fitness. YOLO supports `augment=True` in `model.val()`, which runs inference at multiple scales and flips and averages predictions. No retraining required.

## Updated Evidence — gen_002

**CONFIRMED NON-FUNCTIONAL (research_1 EXP-2):**

Applied `augment=True` to exp5 best.pt. Ultralytics warning: "Model does not support 'augment=True', reverting to single-scale prediction."

Result: mAP50 = 0.8271 — identical to non-TTA baseline. Lift: +0.0000.

The model checkpoint (exp5 best.pt) was exported or saved in a way that disables TTA support. Ultralytics silently falls back to single-scale prediction with only a warning message, producing zero improvement.

## Why It Fails

The exp5 checkpoint was exported to a format that doesn't support TTA, or Ultralytics v8.4.37 has changed TTA behavior for segmentation models. The fallback is silent — no error is raised, no return value indicates the fallback, and the resulting metrics appear normal despite TTA not being applied.

## Implications

This idea cannot provide any evaluation improvement with current weights. The idea as an evaluation-time technique is **debunked**.

## What Would Make This Work

Training a model from scratch with augmentations that support TTA at evaluation time. This would require:
1. A model trained from scratch (not fine-tuned from an exported checkpoint)
2. Possibly avoiding certain export formats (TorchScript, ONNX)
3. Testing TTA compatibility explicitly before relying on it

This is a separate research direction that has not been explored.
