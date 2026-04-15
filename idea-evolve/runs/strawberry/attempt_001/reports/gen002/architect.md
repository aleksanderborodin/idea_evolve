# Architect Report — Generation 2

## Confidence: Medium

The plan is solid given gen 1 data, but there are significant unknowns that could cause the plan to be wrong.

## Data Anomalies

1. **full_1 score (0.8137) exactly matches gen-0 nano baseline** — This is suspicious. If fine-tuning from exp5 for 20 epochs produces the same score as nano from COCO for 20 epochs, either: (a) 20 epochs is the crossover point where exp5's advantage is exhausted, or (b) full_1's lr0 was ignored (confirmed) and the effective lr0=0.000909 was actually slightly worse than COCO training. The optimizer bug masked whether exp5 fine-tune is actually neutral.

2. **yolo11s from COCO outperformed everything** — Gen 1's only success. But it's only 1 data point. We don't know if it's noise or real.

3. **No per-class mAP data** — All 7 disease classes are averaged into one number. The 15x imbalance means we're flying blind on whether improvements target the bottleneck (rare classes) or dominant class.

## What Didn't Fit

- **copy_paste=0.55-0.6 range**: Completely untested. Could have been a quick win but wasn't prioritized. Covered by REC-7 (Architect assigns specific values) but no agent sent to fill this gap.
- **Per-class metrics**: REC-2 from system recommendations — no agent capacity to implement per-class measurement this gen.
- **Training log preservation**: REC-5 — no experimentator to build this diagnostic tool.

## Strategic Risks

1. **All exploitation eggs in one basket**: exploit_1 combines yolo11s + exp5 + AdamW + TTA. If it fails, we won't know which variable caused the failure. May need to run factorial experiments in gen 3.

2. **Resolution hypothesis may be wrong**: imgsz=832 assumes the val-test gap comes from small lesions. But the gap could be from domain shift, lighting differences, or annotation quality — not resolvable by resolution alone.

3. **50-epoch from-scratch (full_1) is the most expensive run**: If it OOMs or crashes, we waste the most time and get zero information.

4. **research_1 must implement TTA manually**: Not available in helpers. If the implementation is buggy, the entire TTA direction gets a false signal.

## Open Questions for System Critic

1. **Is the proxy metric (20 epochs) actually predictive of 100-epoch performance for yolo11s?** We know copy_paste=0.5 lags at 20ep but overtakes at 50-100ep for nano. Does the same pattern hold for yolo11s? If so, 20ep proxy systematically underestimates yolo11s potential.

2. **When should we switch from fine-tune (20ep) to from-scratch (50ep) regime?** The description says 50ep is for "big architectural changes" but yolo11s is an architectural change within the same family. We don't know the threshold.

3. **What is the actual RTX 5060 Ti memory limit for yolo11s at imgsz=832?** If it OOMs, batch=8 is too high. Need to know before launching explore_1.

4. **Should we be targeting val mAP50 or test mAP50 for early stopping?** The proxy metric trains on train, selects best.pt on val, evaluates on test. But if val and test distributions differ (the 0.10 gap), val-based selection might not optimize test performance.
