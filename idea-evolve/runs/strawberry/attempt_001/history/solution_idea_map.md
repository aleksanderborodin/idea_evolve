# Solution-Idea Map — Updated through Generation 2

## Solution sol_001 (score: 0.8137, gen_001 full_1)
- Central: idea_008 (explicit optimizer override — intended but NOT actually implemented due to train_and_eval bug)
- Peripheral: copy_paste=0.5 (established best from exp5)
- Novel elements: First attempt to fine-tune from exp5 with controlled lr0=0.005, but optimizer=auto was passed implicitly so lr0 was ignored.
- Notes: Had large val-test gap (val=0.91, test=0.8137). Score matches gen_0 baseline, suggesting 20-epoch fine-tune is neutral-to-negative vs just using exp5 directly.

## Solution sol_002 (score: 0.8328, gen_001 explore_1)
- Central: idea_001 (yolo11s model scale exploration)
- Peripheral: copy_paste=0.5 (proven best from exp5)
- Novel elements: First use of yolo11s-seg.pt (small model, 3.5x params vs nano) on this problem. Trained from COCO rather than from exp5.
- Notes: BEST SCORE OF GEN_1. yolo11s from COCO outperforms nano baseline at 20 epochs — larger model has more capacity to absorb strawberry domain quickly.

## Solution sol_003 (score: 0.0 INVALID, gen_001 explore_2)
- Central: idea_004 (copy_paste > 0.5 boundary testing)
- Peripheral: None
- Novel elements: copy_paste=0.65 — first attempt above the 0.5 proven value
- Notes: Broken pipe crash. copy_paste=0.65 is unstable or crashes. Not a valid result for scoring but establishes that 0.65 is too high.

## Solution sol_004 (score: 0.8087, gen_002 exploit_1 sol01)
- Central: idea_009 (yolo11s + exp5 via pretrained= flag — but FAILED due to shape mismatch)
- Peripheral: idea_008 (explicit AdamW optimizer), idea_003/idea_011 (TTA at evaluation — non-functional)
- Novel elements: First attempt to combine yolo11s architecture with exp5 domain-adapted weights via pretrained= parameter. Failed silently due to architecture shape mismatch.
- Notes: Score worse than gen-1 best despite correct optimizer and TTA. The pretrained= flag did wholesale weight replacement, not architecture adaptation.

## Solution sol_005 (score: 0.8103, gen_002 exploit_1 sol02)
- Central: idea_008 (explicit AdamW optimizer, properly implemented)
- Peripheral: idea_003/idea_011 (TTA at evaluation — non-functional)
- Novel elements: yolo11n from WEIGHTS_EXP5 directly (correct architecture), explicit AdamW, TTA evaluation. Confirms that 20-epoch fine-tuning from converged checkpoint is neutral.
- Notes: Essentially same score as full_1 (0.8137). Explicit AdamW + TTA did not compensate for lack of training signal from converged checkpoint.

## Solution sol_003 gen_002 (score: 0.5453, gen_002 explore_1 sol01)
- Central: idea_002 (imgsz=832 fine-tuning — DEBUNKED by this result)
- Peripheral: idea_008 (explicit AdamW optimizer)
- Novel elements: First fine-tuning at imgsz=832 from a 640-converged checkpoint. Severe regression confirmed that this specific approach is counterproductive.
- Notes: val mAP50 ≈ 0.91 but test 0.5453 — val-test gap of 0.36. Fine-tuning at a different resolution destroyed domain adaptation. exp5 zero-shot at 832 (0.7876) was much better.

## Baseline (gen_000):
- baseline/sol01: score=0.8137 — nano model, COCO pretrained, 20 epochs (proxy from description.md)
- baseline/sol02: score=0.8175 — nano model, COCO pretrained, 20 epochs (proxy from description.md)

## Research Experiments (gen_002):
- research_1 EXP-1 (score: 0.8271): exp5 best.pt zero-shot, no fine-tuning — highest score achieved in gen_2, confirms fine-tuning marginal benefit
- research_1 EXP-2 (score: 0.8271): TTA on exp5 — identical to non-TTA, confirms TTA non-functional

## Incomplete Solutions:
- explore_1 sol02 (yolo11s from COCO, 40 epochs): NOT EVALUATED — session timeout before evaluation
- full_1 sol01 (yolo11s from COCO, 50 epochs): NOT EVALUATED — evaluation interrupted before completion

## Summary of Idea Implementation
| Solution | Central Ideas | Peripheral Ideas | Novel? | Score |
|----------|--------------|------------------|--------|-------|
| sol_001 gen1 | idea_008 (not implemented — bug) | copy_paste=0.5 | Fine-tune from exp5 with lr0 control | 0.8137 |
| sol_002 gen1 | idea_001 | copy_paste=0.5 | yolo11s from COCO | 0.8328 |
| sol_003 gen1 | idea_004 (failed) | — | copy_paste=0.65 | 0.0 INVALID |
| sol_004 gen2 | idea_009 (FAILED) | idea_008, idea_011 | yolo11s + exp5 via pretrained= | 0.8087 |
| sol_005 gen2 | idea_008 | idea_011 | yolo11n from exp5, AdamW, TTA | 0.8103 |
| sol_003 gen2 | idea_002 (DEBUNKED) | idea_008 | imgsz=832 fine-tune from exp5 | 0.5453 |
| EXP-1 research | idea_012 | — | Zero-shot evaluation | 0.8271 |
| EXP-2 research | idea_011 (DEBUNKED) | — | TTA on exp5 | 0.8271 |
