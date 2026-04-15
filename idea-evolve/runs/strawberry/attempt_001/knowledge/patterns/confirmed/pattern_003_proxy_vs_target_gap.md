---
type: pattern
id: pattern_003
name: "20-epoch proxy mAP50 is ~0.81 vs 0.945 val target"
lifecycle: confirmed
confidence: 0.95
first_seen: gen_001
evidence: ["gen001_explore_1_sol02", "gen001_explore_1_sol04", "gen001_full_1_sol01", "gen001_full_1_sol02"]
related_ideas: []
tags: ["proxy-metric", "epoch-budget", "target-gap"]
---

## Pattern

20-epoch fine-tune from WEIGHTS_EXP5 yields mAP50 ~0.81-0.83, while the full 100-epoch trained WEIGHTS_EXP5 achieved val mAP50=0.945. This means:

1. The 20-epoch proxy captures ~86% of the final performance
2. The gap between proxy (0.81-0.83) and target (0.92) suggests approaches that differentiate at 20 epochs may not maintain advantage at 100 epochs
3. Or: the proxy is systematically biased and needs calibration

## Evidence

Best gen001 proxy score: 0.8296 (explore_1_sol04, 20 epochs)
Target from description: 0.92 (proxy for 100-epoch performance)
WEIGHTS_EXP5 original val: 0.945 (100 epochs)

## Implication for generation 2

The proxy metric may be pessimistic — a config that scores 0.83 at 20 epochs might reach 0.92+ at 100 epochs. However, the relative ordering of configs at 20 epochs may not match the ordering at 100 epochs. This creates uncertainty in interpreting gen1 results.