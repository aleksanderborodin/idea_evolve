# Coverage Matrix

## Top Idea Combinations Tried in Generation 1

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|-----------------|-------------|------------|-----------|------------|
| copy_paste=0.7 alone | 3 | 0.8296 | 0.8210 | gen_001 |
| copy_paste=0.7 + mosaic=0.3 | 1 | 0.8257 | 0.8257 | gen_001 |
| copy_paste=0.7 + mixup=0.15 + low_lr | 1 | 0.8296 | 0.8296 | gen_001 |
| copy_paste=0.8 | 1 | 0.8125 | 0.8125 | gen_001 |
| copy_paste=0.6 + 40 epochs | 1 | 0.8209 | 0.8209 | gen_001 |
| copy_paste=0.5 baseline | 1 | 0.8103 | 0.8103 | gen_001 |
| yolo11s from scratch | 1 | 0.0 (invalid) | 0.0 | gen_001 |
| cls_pw class weighting | 1 | 0.0 (invalid) | 0.0 | gen_001 |

## Unexplored Regions (High Priority for Gen 2)

1. **copy_paste=0.65 with mixup** — sweet spot between 0.6 and 0.7 not tested
2. **WEIGHTS_EXP6 as starting point** — exp6_combined_aug (0.936 val) not tried as fine-tune source
3. **Progressive resolution (320→640)** — mentioned in research but not attempted
4. **Custom class weights via YAML** — direct mechanism to address imbalance not tested
5. **BCE-Dice-Lovász composite loss** — research suggests this but no implementation attempted
6. **yolo11s with fewer epochs (30)** — avoid BrokenPipeError but capture larger model benefit
7. **Staged fine-tuning** (freeze backbone 10 layers, then unfreeze) — not attempted