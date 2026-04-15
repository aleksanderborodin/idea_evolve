# State of Affairs — Generation 1

## Current Standing

**Best:** gen001_explore_1_sol04, mAP50=0.8296 (20-epoch fine-tune from WEIGHTS_EXP5).
Config: copy_paste=0.7, mixup=0.15, lr0=0.0005, mosaic=0.3.

**Population:** 8 solutions evaluated (6 valid, 2 invalid). Gen 1 complete.
**Gap:** Proxy ~0.83 vs target 0.92 (~0.09 uncertainty from proxy reliability and epoch budget).

## What Works

1. **copy_paste=0.7** outperforms both 0.5 and 0.8 for fine-tuning (established, confidence 0.85, 3 solutions)
2. **mixup=0.15 + copy_paste=0.7** synergize: +0.004 over copy_paste alone (active, confidence 0.8, 1 solution)
3. **mosaic=0.3 + copy_paste=0.7** beats either alone (active, confidence 0.85, 1 solution with 2-trial comparison)
4. **lr0=0.0005** stabilizes mixup training (active, confidence 0.7, 1 solution)
5. **WEIGHTS_EXP5** is the only tested starting checkpoint (val mAP50=0.945 at 100 epochs)
6. **Anthracnose improved to 0.858** with mixup — rare classes respond to augmentation, not fundamentally limited

## Coverage Map

**Explored:**
- copy_paste: 0.5, 0.6, 0.7, 0.8 | mixup: 0.15 only | mosaic: 0.0, 0.3
- lr0: 0.001, 0.0005, 0.002 | epochs: 20, 40 | checkpoint: WEIGHTS_EXP5 only

**High-priority unexplored:**
1. WEIGHTS_EXP6 as fine-tune source (0.936 val — untested)
2. copy_paste=0.65 with mixup (sweet spot gap)
3. Progressive resolution (320→640)
4. Staged fine-tuning (freeze/unfreeze backbone)
5. imgsz=832 for small lesions
6. yolo11s (30 epochs, after BrokenPipe fix)
7. Custom class weights via YAML
8. BCE-Dice-Lovász composite loss (loss injection API unknown)

## Dead Ends

1. **cls_pw > 1.0** — YOLO rejects; parameter range is [0, 1], not a multiplier
2. **TTA via augment=True** — YOLO11n-seg silently ignores it in val()
3. **copy_paste=0.8** — over-aggressive; degrades to 0.8125
4. **mosaic=0 entirely** — harmful even with high copy_paste (−0.008)

## Open Questions

1. **Will copy_paste=0.7 advantage hold at 40+ epochs?** Only tested at 20 — proxy may not predict ordering at full training.
2. **Is WEIGHTS_EXP6 a better starting point than WEIGHTS_EXP5?** exp6_combined_aug (0.936 val) completely untested as fine-tune source.
3. **Why is Angular Leafspot universally weak (0.66-0.74)?** No gen1 approach improved it; may need boundary loss or higher resolution.
4. **yolo11s potential?** Training was healthy (trending 0.81 at epoch 40) but eval crashed; model ceiling unknown.
5. **Does 40 epochs on best config reach 0.85+?** Extended training proxy untested.
6. **Is YOLO11 loss injection feasible?** API unknown; requires monkey-patching.
7. **No per-class mAP50 baseline for WEIGHTS_EXP5.** Bottleneck classes (Angular Leafspot, Leaf Spot) have unknown headroom.
8. **Research findings from gen1 not persisted to knowledge base.** Research_1 literature survey exists only in debrief, not accessible to gen2 Architect.

## Strategic Assessment

Gen 1 explored augmentation hyperparameter space thoroughly but left major directions untouched. The bottleneck classes (Angular Leafspot, Leaf Spot) are unaddressed by any approach. Copy_paste tuning alone is unlikely to close the 0.09 gap — WEIGHTS_EXP6, loss engineering, and larger model are the highest-value next steps. The proxy metric (20 epochs) may be unreliable predictor of 100-epoch ordering; treat gen1 relative rankings with caution.
