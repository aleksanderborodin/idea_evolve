# Observations — Full Agent Gen 2

## What I Tried

Single approach: yolo11s from COCO at 50 epochs (PROXY_EPOCHS_SCRATCH) to test whether the larger model's 0.8328 score at 20 epochs was reproducible at full convergence.

## Why This Approach

Gen 1's explore_1 got 0.8328 with yolo11s at 20 epochs — only 1 try, no confirmation. The question was whether this was noise or a real signal. 50 epochs gives the model proper time to converge from scratch, providing a cleaner comparison.

## Result

Could not obtain final score. Evaluation runtimes (~25 min for 50 epochs) exceeded what the environment allowed before interruption. Multiple restart attempts all failed before completion.

## Key Observations

1. **yolo11s downloads correctly**: 10.1M params, 33.1 GFLOPs confirmed
2. **Training starts correctly**: Epoch 1 completed with sensible losses, val mAP50=0.0022 (expected low at start)
3. **AdamW optimizer correctly applied**: lr=0.01 confirmed in logs
4. **Evaluation infrastructure issue**: Long-running processes keep getting interrupted before producing scores

## Failed Experiments

- sol01.py evaluation never completed despite multiple attempts

## Information Lacking

- No completed yolo11s at 50 epochs evaluation result
- No confirmation whether the 0.8328 gen1 result was noise or signal
- The evaluation system appears to have trouble with runs > 15 minutes

## Recommendations for Future Agents

1. Use PROXY_EPOCHS_FINETUNE (20 epochs) instead of PROXY_EPOCHS_SCRATCH (50 epochs) — fits within time budgets
2. Test yolo11s fine-tuning from exp5 checkpoint rather than from-scratch (should converge faster)
3. If testing from-scratch, use 20-epoch budget to stay within time limits