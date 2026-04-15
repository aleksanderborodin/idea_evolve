---
type: idea
id: idea_006
name: "Progressive resolution fine-tuning"
lifecycle: active
confidence: 0.6
first_seen: gen_001
last_updated: gen_002
last_confirmed_gen: gen_001
supported_by: []
contradicted_by: []
related_ideas: [idea_002, idea_010]
cluster: cluster_001
tags: [resolution, staged-training, fine-tuning, imgsz-832]
---

## What It Is

Two-stage fine-tuning: first train at imgsz=640 for 10 epochs (fast convergence on low-res), then unfreeze and train at imgsz=832 for 10 more epochs (refine on high-res details). Total 20 epochs, same budget as standard fine-tuning.

## How It Works

The model first learns coarse disease features at 640 (fast, stable), then refines mask boundaries at 832 without having to learn from scratch at high resolution. Staging avoids the cold-start problem of training at 832 from epoch 0.

## Why This Is More Promising Than Direct imgsz=832 Fine-Tuning

Direct fine-tuning at 832 from a 640-converged checkpoint was debunked in gen_002 (explore_1 sol01: 0.5453 regression). The staged approach should work better because:
1. Stage 1 (640): Model learns domain features at its native resolution — stable, fast
2. Stage 2 (832): Model has domain knowledge already; now adapts spatial resolution without losing what it learned
3. The domain adaptation from 640 training is preserved when transitioning to 832

## Evidence

- gen_002 proved that 20 epochs of direct 832 fine-tuning from a 640-converged checkpoint destroys domain knowledge (0.5453 vs 0.7876 zero-shot at 832)
- Progressive resizing is a known technique in deep learning that avoids the domain disruption seen in direct resolution switching
- **No agent has implemented this yet** — it remains the most promising unexplored approach for resolution adaptation

## Implementation

```python
# Stage 1: 640 for 10 epochs
model.train(data=DATA_V1, epochs=10, imgsz=640, ...)
best640 = RUN_DIR / "weights" / "best.pt"
# Stage 2: 832 for 10 epochs
model2 = YOLO(str(best640))
model2.train(data=DATA_V1, epochs=10, imgsz=832, batch=8, ...)
```

## Risks

- Must use cleanup=False between stages to preserve intermediate checkpoint
- Stage 2 lr should be lower (0.0005) since model is already partially converged
- This approach takes 2x the training time (10 + 10 epochs with two separate training calls)
- Within a 20-epoch budget, this gives only 10 epochs at each resolution, which may still be insufficient

## Staleness Note

This idea has never been tested. last_confirmed_gen remains gen_001. Confidence of 0.6 reflects untested status — it could rise with successful implementation or drop if attempted and failed.
