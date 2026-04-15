---
type: pattern
id: pattern_001
name: "copy_paste=0.7-0.8 sweet spot for fine-tuning"
lifecycle: confirmed
confidence: 0.85
first_seen: gen_001
evidence: ["gen001_explore_1_sol02", "gen001_explore_1_sol03", "gen001_explore_1_sol04", "gen001_explore_1_sol05", "gen001_full_1_sol02"]
related_ideas: ["idea_001", "idea_002", "idea_003"]
tags: ["augmentation", "copy-paste", "fine-tuning"]
---

## Pattern

copy_paste=0.7 appears to be the sweet spot for fine-tuning from WEIGHTS_EXP5. Values of 0.5 (baseline) and 0.8 (higher) both underperform 0.7 in the 20-epoch fine-tune setting.

## Data

| copy_paste | mosaic | mixup | lr0 | mAP50 | Solution |
|------------|--------|-------|-----|-------|----------|
| 0.5 | 0.0 | 0 | 0.001 | 0.8103 | full_1_sol01 |
| 0.6 | 0.0 | 0 | 0.001 | 0.8209 | full_1_sol02 (40ep) |
| 0.7 | 0.3 | 0 | 0.001 | 0.8257 | explore_1_sol02 |
| 0.7 | 0.15 | 0.15 | 0.0005 | 0.8296 | explore_1_sol04 |
| 0.7 | 0.0 | 0 | 0.001 | 0.8177 | explore_1_sol05 |
| 0.8 | 0.0 | 0 | 0.002 | 0.8125 | explore_1_sol03 |

## Interpretation

The augmentation space around copy_paste=0.7 + mosaic=0.3 + mixup=0.15 + lr0=0.0005 is the current frontier for fine-tuning approaches.