---
type: idea
id: idea_001
name: "yolo11s from COCO — larger model outperforms nano at 20 epochs"
lifecycle: established
confidence: 0.8
first_seen: gen_001
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: [sol_002]
contradicted_by: []
related_ideas: [idea_009, idea_010]
cluster: cluster_001
tags: [model-scale, larger-model, from-coco]
---

## What It Is

Training yolo11s-seg.pt (10.1M params, 3.5x nano) from COCO pretrained weights for 20 epochs achieves mAP50=0.8328 — outperforming nano at the same epoch count (0.8137-0.8175). The larger model has more capacity to absorb the strawberry domain quickly.

## Current Evidence

- gen_001 sol_002 (explore_1): yolo11s from COCO, 20 epochs → mAP50=0.8328 (BEST SCORE OF RUN)
- gen_0 baseline: yolo11n from COCO, 20 epochs → mAP50=0.8137-0.8175

## Important Clarification

This idea is about yolo11s **from COCO**, not from exp5. The idea "yolo11s fine-tuned from exp5 checkpoint" is a SEPARATE untested hypothesis — the exp5 weights are yolo11n architecture and cannot be loaded into yolo11s via pretrained= flag (idea_009).

## When It Helps

The larger model provides more representation capacity. In 20-epoch proxy regime, yolo11s from COCO outperforms both nano from COCO and nano/small from exp5 fine-tuning.

## Open Questions

- Does yolo11s from COCO benefit from more than 20 epochs? (40ep and 50ep attempts timed out before evaluation — weights may exist on disk)
- Does yolo11s from COCO at imgsz=832 (from-scratch, not fine-tuning) capture small lesions better?
- Does the larger model need different learning rate or batch size?
