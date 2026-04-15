---
type: cluster
id: cluster_003
name: "Training dynamics and reliability"
member_ideas: [idea_004, idea_005, idea_007, idea_008, idea_009, idea_012]
best_score: 0.8103
best_solution: exploit_1 sol02 (gen_2)
status: active
last_updated: gen_002
---

Ideas about training mechanics, optimizer behavior, and known failure modes.

gen_2 additions:
- idea_009 (yolo11s + exp5 via pretrained= flag): Debunked — the pretrained= parameter does wholesale weight replacement, not architecture adaptation. yolo11n weights cannot be loaded into yolo11s architecture.
- idea_012 (fine-tuning marginal benefit): Established — zero-shot exp5 (0.8271) nearly matches best fine-tuned result (0.8328). The marginal value of 20-epoch fine-tuning in proxy regime is only +0.0057.

Key findings:
1. optimizer='auto' ignores explicit lr0 — must use optimizer='AdamW' explicitly (idea_005, established)
2. copy_paste > 0.5 causes crashes/instability (idea_004, established)
3. 20-epoch fine-tuning from converged checkpoint produces val-test gap (idea_007, established)
4. Architecture mismatch between model and checkpoint cannot be bridged via pretrained= flag (idea_009, debunked)
5. Fine-tuning provides marginal benefit in 20-epoch proxy regime (idea_012, established)

**Note on best_score:** The cluster's best_score (0.8103) reflects the best scored solution using cluster ideas (exploit_1 sol02: yolo11n from exp5, AdamW, TTA). The higher score of 0.8271 (research_1 EXP-1: zero-shot exp5) is not a training-dynamics result — it's a direct evaluation without training. The cluster_001 best (0.8328 from yolo11s from COCO) uses model-scale ideas, not training-dynamics ideas per se (though it does use copy_paste=0.5).
