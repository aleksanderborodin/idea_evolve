## Current Population Status
Best solution: No solutions evaluated yet (gen 1 cold start)
Second best: N/A

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/description.md` — Problem definition and key findings
- Note: Prior experiments (exp1-exp8) found copy_paste=0.5 to be the best augmentation strategy (val mAP50=0.945 at 100 epochs). This is the starting point.

## Directive
This is a Track B radical exploration. You must NOT use the current dominant technique as your starting point.

**Task: Explore higher copy-paste values (0.6-0.8) combined with class-aware sampling.**

Prior experiments tested copy_paste=0.5 (exp5, best) and copy_paste=0.3 (exp6). The 15x class imbalance (Leaf Spot: 1365 vs Anthracnose: 89) is the core challenge. Your job is to push copy-paste further AND address the imbalance more aggressively:

1. Use `train_and_eval` with `copy_paste=0.6` or `copy_paste=0.7`
2. Add class-aware sampling: upweight rare classes via `cls_pw` parameter or custom class weights
3. Try combining higher copy_paste with `mosaic=0.3` to reduce noise from mixing too many images
4. Keep everything else conservative (lr0=0.001, AdamW, 20 epochs fine-tune from exp5)

Do NOT try training from scratch (yolo11n-seg.pt) — save that for a different direction. Focus on squeezing more from the fine-tune path.

Baseline to beat: exp5_copy_paste=0.5 achieved val mAP50=0.945 at 100 epochs (proxy baseline ~0.92).
