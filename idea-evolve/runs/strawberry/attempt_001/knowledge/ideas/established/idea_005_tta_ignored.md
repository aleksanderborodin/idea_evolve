---
type: idea
id: idea_005
name: "TTA silently ignored on YOLO11n-seg val()"
lifecycle: established
confidence: 1.0
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: ["gen001_explore_1_sol03", "gen001_full_1_sol01", "gen001_full_1_sol02"]
contradicted_by: []
related_ideas: []
cluster: null
tags: ["TTA", "test-time-augmentation", "YOLO11n-limitation"]
---

## What

YOLO11n-seg does not support test-time augmentation in val mode. Passing `augment=True` to `model.val()` logs a warning and reverts to single-scale evaluation.

## Evidence

- gen001_explore_1_sol03: tta=True → mAP50=0.8125 (not better than sol02 without TTA)
- gen001_full_1_sol01: tta=True → mAP50=0.8103
- gen001_full_1_sol02: tta=True → mAP50=0.8209

The description.md and helpers claim TTA adds ~0.5-2%, but YOLO11n-seg appears to not support it in val mode. The warning goes to stderr and may not be visible to agents.

## Implication

TTA via `model.val(augment=True)` is not working as documented for YOLO11n-seg. Agents should not expect TTA benefit when using the nano model.

## Alternative

May need to implement TTA manually via multiple predict calls with different scales/flips and average results.