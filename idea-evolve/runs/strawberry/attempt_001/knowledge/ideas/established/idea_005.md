---
type: idea
id: idea_005
name: "optimizer=auto ignores explicit lr0"
lifecycle: established
confidence: 0.9
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: [sol_001]
contradicted_by: []
related_ideas: [idea_008]
cluster: cluster_003
tags: [optimizer, learning-rate, bug, training]
---

## What It Is

When using `train_and_eval()` (which passes optimizer='auto' to YOLO), explicit `lr0=X` settings are silently ignored. YOLO's auto-optimizer ignores lr0 and momentum and picks its own settings (found: lr=0.000909 AdamW).

## How It Works

The `train()` call passes `optimizer='auto'` as a default in `train_and_eval`. When this is set, YOLO determines optimizer, lr0, and momentum automatically — the explicit lr0 in the caller's kwargs is ignored with a logged warning.

## Current Evidence

- gen_001 full_1 (sol01): specified lr0=0.005, YOLO logged "optimizer: 'optimizer=auto' found, ignoring 'lr0=0.005' and 'momentum=0.937'" and used lr=0.000909 instead. Score: 0.8137.
- gen_0 baseline sol01 (similar settings): 0.8137 — virtually identical, confirming lr0 was ignored in both.

## When It Hurts

Agents think they're testing a specific lr0 but actually get auto-selected lr. This confounds interpretation of results and wastes experiments testing lr values that have no effect.

## How to Override

Always pass `optimizer='AdamW'` explicitly when you want to control lr0:
```python
train_and_eval(model_path, lr0=0.005, optimizer='AdamW', ...)
```
