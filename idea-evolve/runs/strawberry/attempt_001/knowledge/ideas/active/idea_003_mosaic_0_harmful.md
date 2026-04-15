---
type: idea
id: idea_003
name: "mosaic=0 is harmful even with high copy_paste"
lifecycle: active
confidence: 0.85
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: ["gen001_explore_1_sol05"]
contradicted_by: []
related_ideas: ["idea_001"]
cluster: null
tags: ["augmentation", "mosaic", "class-imbalance"]
---

## What

Disabling mosaic entirely (mosaic=0) with high copy_paste=0.7 degrades performance compared to mosaic=0.3 + copy_paste=0.7.

## Evidence

- gen001_explore_1_sol02: copy_paste=0.7, mosaic=0.3 → mAP50=0.8257
- gen001_explore_1_sol05: copy_paste=0.7, mosaic=0.0 → mAP50=0.8177 (−0.008)

## Why

Mosaic creates composited training samples with diversity that copy-paste alone cannot replicate. Even a reduced mosaic (0.3) provides benefit — the two augmentation strategies are complementary, not redundant.

## Implication

Agents should not disable mosaic when using copy-paste. The combination mosaic=0.3 + copy_paste=0.7 is better than either alone.
