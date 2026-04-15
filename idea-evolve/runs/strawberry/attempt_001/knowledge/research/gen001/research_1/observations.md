# Observations — Research Agent Gen 1

## Context
Research mission for strawberry disease segmentation. No prior generation has run. No papers in the papers/ directory. All knowledge comes from description.md, initial_facts.md, initial_ideas.md, and helpers/core.py.

## Key Observations

1. **Problem is well-scoped but under-explored**: 8 prior experiments (exp1-exp8) all used the same model size (yolo11n-seg) and same resolution (640). Only one technique (copy_paste) was identified as highly effective. The search space for model size, resolution, loss functions, and evaluation-time techniques is essentially untouched.

2. **Class imbalance is the central challenge**: 15x between Leaf Spot and Anthracnose. Every technique should be evaluated for its impact on rare-class performance, not just overall mAP50.

3. **No existing papers in the library**: The papers/ directory is empty. There's no structured academic knowledge about this specific problem. All prior "research" was empirical hyperparameter tuning.

4. **evaluate.py is well-engineered**: The GPU lock, caching, and venv re-exec are all robust. I had no issues understanding the evaluation pipeline. The helpers/core.py `train_and_eval` function is clean and saves a lot of boilerplate.

5. **The 6 techniques I investigated are all implementable**: None require architectural changes to YOLO or hacky workarounds. TTA, progressive resizing, label smoothing, and NMS tuning are all native Ultralytics features. Class weighting is implementable with moderate effort. Ensemble is the most complex but still tractable.

6. **Proxy epoch budget is tight**: 20 epochs fine-tuning from a converged 100-epoch model means most gains will come from improved evaluation techniques (TTA, NMS tuning) rather than new training dynamics. The model is already near convergence.

7. **Larger models (yolo11s, yolo11m) untested**: The description mentions RTX 5060 Ti has 16GB VRAM — yolo11s-seg runs fine at batch=16. No experiment tested this. This is likely the single highest-impact untested change.

## What's Missing
- No academic papers on this specific strawberry disease dataset
- No per-class performance breakdowns in the experiment results (only overall mAP50)
- No analysis of failure modes (what does the model get wrong?)
- No understanding of whether small disease spots vs. large outbreaks dominate the error
