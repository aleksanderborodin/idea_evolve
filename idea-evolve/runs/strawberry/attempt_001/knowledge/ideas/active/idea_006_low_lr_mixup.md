---
type: idea
id: idea_006
name: "lower learning rate (lr0=0.0005) helps with mixup"
lifecycle: active
confidence: 0.7
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: ["gen001_explore_1_sol04"]
contradicted_by: []
related_ideas: ["idea_002"]
cluster: null
tags: ["learning-rate", "hyperparameter", "mixup"]
---

## What

Using lr0=0.0005 (lower than default 0.001) combined with mixup=0.15 and copy_paste=0.7 produced the best result in gen001.

## Evidence

gen001_explore_1_sol04: copy_paste=0.7, mixup=0.15, lr0=0.0005 → mAP50=0.8296

vs sol02: copy_paste=0.7, mosaic=0.3, lr0=0.001 → mAP50=0.8257

## Why

Mixup introduces additional regularization that may require a lower learning rate to avoid destabilizing training. The combination of mixup + lower lr0 seems to provide better convergence.

## Unknown

Whether lr0=0.0005 helps without mixup, or whether this is a synergistic effect specific to the mixup+copy_paste combination.
