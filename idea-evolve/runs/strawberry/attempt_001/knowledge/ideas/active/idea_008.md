---
type: idea
id: idea_008
name: "Explicit optimizer override (AdamW)"
lifecycle: active
confidence: 0.8
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: [sol_001]
contradicted_by: []
related_ideas: [idea_005]
cluster: cluster_003
tags: [optimizer, learning-rate, training-control]
---

## What It Is

Always pass `optimizer='AdamW'` explicitly in `train_and_eval()` calls when you need to control the learning rate. Without this, YOLO's auto-optimizer ignores lr0 and momentum settings.

## How It Works

Setting `optimizer='AdamW'` forces YOLO to use AdamW with the provided lr0, rather than auto-selecting. This gives agents true control over the learning rate schedule.

## Current Evidence

- gen_001 full_1 tried lr0=0.005 but got lr=0.000909 because optimizer='auto' was used
- No solution has yet tested this idea with proper optimizer override

## Implementation

```python
train_and_eval(
    model_path=WEIGHTS_EXP5,
    epochs=20,
    optimizer='AdamW',  # CRITICAL: must be explicit
    lr0=0.005,
    copy_paste=0.5,
)
```

## When It Helps

Any experiment that wants to test a specific learning rate must use this. Also enables proper comparison between lr0=0.001 vs lr0=0.005 vs lr0=0.01.
