---
type: idea
id: idea_002
name: "mixup+copy_paste synergy"
lifecycle: active
confidence: 0.8
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: ["gen001_explore_1_sol04"]
contradicted_by: []
related_ideas: ["idea_001", "idea_006"]
cluster: null
tags: ["augmentation", "mixup", "synergy"]
---

## What

Combining mixup=0.15 with copy_paste=0.7 produces the best result in gen001 (mAP50=0.8296), outperforming copy_paste alone.

## Evidence

gen001_explore_1_sol04: copy_paste=0.7 + mixup=0.15 + lr0=0.0005 → mAP50=0.8296 (best in gen001)

Per-class breakdown shows Anthracnose (rarest class) improved to 0.858 — best across all gen001 solutions.

## Why it works

Mixup provides a different kind of augmentation than copy-paste. Where copy-paste composites existing annotations, mixup blends images and their labels. The combination provides complementary regularization that better addresses the class imbalance without over-augmenting.

## Unknown

Optimal mixup value — only tested mixup=0.15. Could be improved with sweep.
Whether this holds at 40 epochs (only tested at 20).
