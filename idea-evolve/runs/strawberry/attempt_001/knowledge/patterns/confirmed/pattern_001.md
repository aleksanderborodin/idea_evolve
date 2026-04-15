---
type: pattern
id: pattern_001
name: "yolo11s from COCO outperforms nano baseline at 20 epochs"
lifecycle: confirmed
confidence: 0.7
first_seen: gen_001
evidence: [sol_002]
related_ideas: [idea_001]
tags: [model-scale, yolo11s, from-scratch]
---

At 20 epochs training from COCO pretrained weights, yolo11s-seg (10.1M params) achieved mAP50=0.8328, outperforming the nano model baseline at the same epoch count (0.8137-0.8175). This is the opposite of what was expected — the larger model generalizes better in the short-training regime when starting from COCO, possibly because it has more representation capacity to absorb the strawberry domain from scratch in limited epochs.
