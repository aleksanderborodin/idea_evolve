# State of Affairs — Generation 2 (Rewrite)

## Current Standing

Best score: **0.8328** (gen_001 explore_1, yolo11s-seg from COCO pretrained, 20 epochs, copy_paste=0.5). Gen 2 produced zero improvement — best gen 2 score is 0.8271 (research_1 EXP-1, exp5 zero-shot). Gen 2 was a strategic redirection: three major directions were closed simultaneously (TTA non-functional, imgsz=832 fine-tuning catastrophic, yolo11s+exp5 via pretrained= blocked by architecture mismatch). Trajectory: **plateaued**. Two high-value solutions (explore_1 sol02: yolo11s 40 epochs; full_1 sol01: yolo11s 50 epochs) timed out before evaluation — their weights may still exist on disk.

## What Works

- **yolo11s from COCO at 20 epochs** (idea_001, established, confidence 0.8): mAP50=0.8328. Larger model generalizes faster in short-training regime vs nano at same epoch count. NOT the same as "yolo11s from exp5" — that combination has never been tested.
- **optimizer=auto ignores lr0** (idea_005, established, confidence 0.9): Must pass optimizer='AdamW' explicitly. Full_1 gen_1 had val=0.91, test=0.8137 because lr0 was silently ignored.
- **copy_paste ceiling below 0.65** (idea_004, established, confidence 0.7): 0.65 crashes. Do not exceed 0.6. Range 0.55-0.6 unexplored.
- **Val-test gap worsens with fine-tuning** (idea_007, established, confidence 0.9): Additional fine-tuning from converged checkpoint adapts to val without improving test. Zero-shot exp5 has smaller gap (~0.08) than fine-tuned models (~0.10-0.36).
- **Fine-tuning marginal in proxy regime** (idea_012, established, confidence 0.95): Zero-shot exp5 (0.8271) vs best fine-tuned (0.8328, +0.0057 only). Incremental fine-tuning cannot reach 0.92+.

## Current Frontier

Three highest-priority untested experiments:
1. **yolo11s from COCO at 40+ epochs**: Does 0.8328 hold with more training? Two solutions timed out before evaluation — check if weights exist on disk.
2. **Progressive resizing 640→832** (idea_006): Direct 832 fine-tuning destroyed domain knowledge (0.5453 regression). Staged approach (10 epochs at 640, then 10 at 832) may preserve adaptation while testing resolution hypothesis.
3. **Class imbalance investigation**: 15x ratio (Leaf Spot vs Anthracnose). Per-class mAP50 is unavailable — aggregate score hides which classes are limiting. Class-weighted copy_paste is unexplored.

## Coverage Map

| Idea | Status | Trials | Best Score |
|------|--------|--------|------------|
| yolo11s from COCO (idea_001) | established | 1 | 0.8328 |
| copy_paste=0.65 (idea_004) | debunked (crashed) | 1 | 0.0 |
| optimizer=auto bug (idea_005) | established | 1 | 0.8137 |
| imgsz=832 fine-tune (idea_010) | debunked | 1 | 0.5453 |
| TTA evaluation (idea_003/011) | debunked | 2 | 0.8271 (no lift) |
| yolo11s+exp5 via pretrained= (idea_009) | debunked | 1 | 0.8087 |
| Zero-shot exp5 (idea_012) | established | 1 | 0.8271 |
| Progressive resizing (idea_006) | active | 0 | — |
| AdamW explicit (idea_008) | active | 1 | 0.8103 |

**Well-explored:** nano from COCO (gen_0 baseline 0.81-0.83). **Dead directions:** TTA, pretrained= across architectures, direct 832 fine-tuning. **Under-explored:** yolo11s from COCO at longer epochs, progressive resizing, class weighting.

## Dead Ends

1. **TTA is non-functional** (idea_003/011): exp5 silently reverts to single-scale with only a warning. Zero lift. Fresh training required to enable TTA.
2. **imgsz=832 fine-tuning destroys domain knowledge** (idea_010): 0.5453 vs 0.7876 zero-shot at same resolution. Domain adaptation is resolution-specific and is wiped by 20 epochs at a new resolution.
3. **pretrained= across architectures fails silently** (idea_009): yolo11n weights cannot load into yolo11s via pretrained= flag. Wholesale weight replacement, not fine-tuning. Score 0.8087.
4. **20-epoch fine-tuning from converged checkpoint is neutral** (idea_012): All attempts score ~0.81, matching or below zero-shot. The proxy regime cannot absorb more fine-tuning productively.

## Open Questions

1. **Does yolo11s from COCO benefit from more than 20 epochs?** Two attempts (40ep, 50ep) timed out. If weights on disk, evaluate immediately. If not, retry with shorter training.
2. **Does progressive resizing preserve domain while adapting resolution?** Only untested approach that could make imgsz=832 work without destroying learned features.
3. **Is class imbalance the actual bottleneck?** 15x Leaf Spot vs Anthracnose ratio. No per-class mAP data exists. If rare classes are limiting, targeted augmentation (class-weighted copy_paste) could unlock disproportionate gains.
4. **Why is fine-tuning marginal?** Zero-shot exp5 (0.8271) nearly matches best fine-tuned (0.8328). Is the convergence plateau real, or does yolo11s from COCO with 40+ epochs break through?
5. **What caused explore_2's crash?** Single observation at copy_paste=0.65 with broken pipe. CUDA failure vs copy_paste-specific unknown.
6. **Can TTA work with fresh training?** EXP-2 showed exp5 doesn't support TTA. Whether a freshly trained model enables it is untested.
