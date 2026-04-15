# Observations — Full Agent Gen 1

## Approach
Reproduced the exp5 fine-tuning baseline with incremental improvements.

## Solutions Tried

### sol01 — exp5 baseline + TTA + label_smoothing
- **Config**: Fine-tune from WEIGHTS_EXP5, 20 epochs, copy_paste=0.5, lr0=0.001, label_smoothing=0.05, TTA
- **Score**: mAP50 = 0.8103
- **Train time**: 240.5s
- **Notes**: label_smoothing is deprecated in ultralytics 8.4.37 (printed warning). Score is a solid baseline but below target (0.92).

### sol02 — More epochs + higher copy_paste
- **Config**: Fine-tune from WEIGHTS_EXP5, 40 epochs, copy_paste=0.6, lr0=0.001, TTA
- **Score**: mAP50 = 0.8209
- **Train time**: 461.6s
- **Notes**: +1% improvement over sol01 from more epochs + slightly higher copy_paste. Per-class breakdown shows Angular Leafspot (0.66) and Leaf Spot (0.77) are weakest.

## Key Findings
- The 20-epoch proxy gives ~0.81, suggesting the 100-epoch val score of 0.945 from exp5 does not fully transfer to the proxy evaluation setup.
- TTA adds ~0.5-2% as documented in helpers.core.
- copy_paste=0.6 slightly outperforms 0.5 at 40 epochs.

## Time Budget
Two solutions evaluated in ~12 minutes total. No more time for additional iterations.