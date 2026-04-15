# Coverage Matrix — Generation 2

## Sparse Matrix (ideas with actual coverage)

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|-----------------|------------|-----------|-----------|------------|
| idea_001 alone (yolo11s from COCO) | 1 | 0.8328 | 0.8328 | gen_001 |
| idea_002 + idea_008 (imgsz=832 fine-tune + AdamW) | 1 | 0.5453 | 0.5453 | gen_002 |
| idea_002 + idea_010 (imgsz=832 — DEBUNKED) | 1 | 0.5453 | 0.5453 | gen_002 |
| idea_003 alone (TTA — DEBUNKED) | 1 | 0.8271 | 0.8271 | gen_002 |
| idea_008 + idea_011 (AdamW + TTA on yolo11n from exp5) | 1 | 0.8103 | 0.8103 | gen_002 |
| idea_009 (yolo11s + exp5 via pretrained= — DEBUNKED) | 1 | 0.8087 | 0.8087 | gen_002 |
| idea_012 alone (zero-shot exp5) | 1 | 0.8271 | 0.8271 | gen_002 |
| copy_paste=0.5 alone (baseline) | 2 | 0.8175 | 0.8156 | gen_000 |
| idea_004 alone (copy_paste=0.65 — crashed) | 1 | 0.0 (invalid) | — | gen_001 |

## Ideas with Zero Coverage (untested or not fully tested)
- idea_006: progressive resolution fine-tuning (promising but not implemented)
- idea_007: val-test gap investigation (pattern confirmed but no solution specifically addresses it)
- idea_001 + idea_012: yolo11s from exp5 checkpoint (most important untested combination)
- idea_001 + idea_002: yolo11s from COCO at imgsz=832 (from-scratch, not fine-tuning)
- idea_006 + idea_001: yolo11s progressive resizing

## Key Observations — gen_2
1. **The search space remains largely unexplored** — most idea combinations have not been tested
2. **TTA is dead** — idea_003 and idea_011 are debunked. No evaluation-time improvements are available.
3. **imgsz=832 fine-tuning is counterproductive** — direct fine-tuning at different resolution from converged checkpoint is debunked
4. **Fine-tuning from converged checkpoint provides marginal benefit** — idea_012 established at 0.95 confidence
5. **Architecture mismatch is a hard constraint** — yolo11n weights cannot be loaded into yolo11s via pretrained= flag
6. **The best path forward** is yolo11s from COCO with longer training (40+ epochs) or progressive resizing from 640→832

## Recommendations for Next Generation
- Highest priority: yolo11s from COCO with 40+ epochs (yolo11s from COCO at 20ep = 0.8328; need to confirm with more training)
- Try progressive resizing (idea_006): train 640, then fine-tune 832
- Drop all TTA-related planning — it's non-functional
- Drop yolo11s + exp5 combination via pretrained= — architecture mismatch is insurmountable
- Consider yolo11s from COCO at imgsz=832 from-scratch (not fine-tuning) to test resolution hypothesis cleanly
