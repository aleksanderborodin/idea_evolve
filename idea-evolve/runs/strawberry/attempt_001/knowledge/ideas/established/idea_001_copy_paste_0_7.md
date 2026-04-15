---
type: idea
id: idea_001
name: "copy_paste=0.7 outperforms 0.5 and 0.8"
lifecycle: established
confidence: 0.85
first_seen: gen_001
last_updated: gen_001
last_confirmed_gen: gen_001
supported_by: ["gen001_explore_1_sol02", "gen001_explore_1_sol04", "gen001_explore_1_sol05"]
contradicted_by: []
related_ideas: ["idea_002", "idea_003"]
cluster: null
tags: ["augmentation", "copy-paste", "class-imbalance"]
---

## What

Fine-tuning from WEIGHTS_EXP5 with copy_paste=0.7 (higher than the known best of 0.5 from exp5) yields better mAP50 than copy_paste=0.5 or 0.8.

## Evidence

- gen001_explore_1_sol02: copy_paste=0.7, mosaic=0.3 → mAP50=0.8257
- gen001_explore_1_sol04: copy_paste=0.7, mixup=0.15 → mAP50=0.8296 (best)
- gen001_explore_1_sol05: copy_paste=0.7, mosaic=0.0 → mAP50=0.8177
- gen001_full_1_sol02: copy_paste=0.6, 40 epochs → mAP50=0.8209
- gen001_explore_1_sol03: copy_paste=0.8 → mAP50=0.8125 (degraded)

## Why it works

copy_paste directly addresses the 15x class imbalance (Anthracnose: 89 instances vs Leaf Spot: 1365). A value of 0.7 provides stronger augmentation for minority classes than 0.5 without becoming over-aggressive like 0.8 (which generates unrealistic compound masks).

## Current evidence gap

Only tested on 20-epoch fine-tune from WEIGHTS_EXP5. Unknown if copy_paste=0.7 would outperform 0.5 in full 100-epoch training. The proxy evaluation gives ~0.81-0.83 vs the target of 0.92 for 100-epoch performance.

## Next steps to confirm

Run copy_paste=0.7 for 40 epochs (PROXY_EPOCHS_EXTENDED) to see if the improvement holds at longer training.
