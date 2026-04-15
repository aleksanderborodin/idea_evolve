## Current Population Status
Best solution: None yet — generation 1. Prior experiments (exp1-exp8) explored augmentation, learning rate, model size (n only), and self-collected data. No experiments tested: TTA, ensemble, progressive resizing, larger models, or custom loss functions.

## Read first
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/description.md
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/initial_ideas.md
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/initial_facts.md

## Directive

This is a **Track B research mission** — find approaches the system has never tried.

**Research scope:** Survey techniques that could improve instance segmentation mAP50 on a class-imbalanced dataset (15x between Leaf Spot and Anthracnose). Focus on:

1. **Test-Time Augmentation (TTA)** — Can multi-scale or flipped inference boost test mAP without retraining?
2. **Ensemble methods** — Train multiple models with different seeds/augmentations, average predictions
3. **Progressive resizing** — Train at 640 then 832 to capture fine disease details
4. **Custom class weighting** — Address imbalance via loss weight modification (beyond copy-paste)
5. **Label smoothing** — Mentioned in description but never tested
6. **NMS tuning** — Different confidence/IoU thresholds for the 7-class problem

**Deliverable:** Write a findings report to `output/report.md` that:
- Describes each technique with enough detail for an agent to implement it
- Identifies which 2-3 techniques are most promising for this specific dataset
- Notes any risks or gotchas (e.g., TTA adds inference time, ensemble needs multiple trained models)

**Constraints:**
- Focus on techniques NOT tested by prior experiments (exp1-exp8)
- Do NOT just describe copy_paste variations — that's already well-explored
- Do NOT suggest yolo11n-seg changes — all nano experiments are documented

**Output:** Write findings to `output/report.md`. This feeds into future generations' coverage matrix and idea base.