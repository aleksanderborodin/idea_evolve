---
type: idea
id: idea_012
name: "Zero-shot exp5 nearly matches best fine-tuned result — fine-tuning provides marginal proxy benefit"
lifecycle: established
confidence: 0.95
first_seen: gen_002
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: [sol_006]
contradicted_by: []
related_ideas: [idea_007]
cluster: cluster_003
tags: [fine-tuning, marginal-benefit, zero-shot, proxy-regime]
---

## What It Is

The observation that the exp5 converged checkpoint (100-epoch, fine-tuned with copy_paste=0.5) achieves mAP50 = 0.8271 on the test set with ZERO additional fine-tuning — only 0.0057 below the best 20-epoch fine-tuned result (0.8328 from yolo11s from COCO).

## How It Works

In the 20-epoch proxy evaluation regime, models start very close to their asymptotic performance. The marginal value of additional fine-tuning is minimal because:
1. The model has already converged to its performance plateau at 100 epochs
2. 20 more epochs of fine-tuning cannot substantially improve on a model that has already learned the domain
3. The adaptation from 20 epochs of fine-tuning is mostly adaptation to val split characteristics, not generalizable improvement

## Evidence

- research_1 EXP-1: exp5 best.pt zero-shot on test: mAP50 = 0.8271
- Gen-1 best (explore_1): yolo11s from COCO, 20 epochs fine-tuning: mAP50 = 0.8328
- Gap: only +0.0057 from 20 epochs of fine-tuning

This confirms that the 20-epoch proxy regime systematically underestimates the value of the converged checkpoint and overestimates the value of additional fine-tuning.

## Implications for Strategy

1. **The path to 0.92+ cannot rely on incremental fine-tuning from exp5** — the marginal gain is too small
2. **Architectural changes (yolo11s from COCO) provide more lift than fine-tuning continuity** — yolo11s achieved 0.8328 vs 0.8137 nano despite both being fine-tuned
3. **Longer training (40-50 epochs) from a better starting point** is the most promising direction
4. **The val-test gap of ~0.10 (val=0.91, test=0.8137)** is a real phenomenon where val improvement doesn't transfer to test — further fine-tuning exacerbates this

## What This Means for Future Generations

Agents should NOT expect incremental improvements from continuing to fine-tune from exp5 with 20-epoch budgets. The most promising experiments are:
- yolo11s from COCO with 40+ epochs (higher model scale + longer training)
- Progressive resizing (train 640, fine-tune 832)
- Class-weighted approaches for rare disease handling
