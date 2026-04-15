## Current Population Status
Best solution: None yet — this is generation 1, no solutions evaluated inside idea-evolve.
Reference point: Prior experiments show exp5 (copy_paste=0.5, 100 epochs) achieved val mAP50=0.945.

## Read first
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/description.md
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/helpers/core.py
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/initial_ideas.md

## Directive

This is a **Track B radical exploration** — you MUST explore a genuinely different direction from all prior experiments.

All 8 prior experiments (exp1-exp8) used `yolo11n-seg.pt` (nano model, 2.9M params). Try `yolo11s-seg.pt` (small model, 10.1M params) as a drop-in replacement. This is a completely different model scale that has never been tested.

**What to do:**
1. Start from WEIGHTS_EXP5 (best known checkpoint) or WEIGHTS_BASE (COCO pretrained) — your choice
2. Fine-tune yolo11s-seg.pt for 20 epochs (PROXY_EPOCHS_FINETUNE=20)
3. Key parameters to test: `copy_paste=0.5` (proven best from exp5), `imgsz=640`, `batch=8` (s model needs less batch)
4. Use `train_and_eval()` helper from helpers.core
5. Return the full metrics dict with mAP50 as fitness

**Constraints:**
- You MUST NOT use yolo11n-seg.pt — that model size has been fully explored by prior experiments
- Do NOT combine multiple augmentation changes — test yolo11s model scale as the single variable
- Use the venv Python: `/home/sasha/Desktop/idea_evolve/first_project/venv/bin/python`

**Output:** Write your solution to `output/sol01.py` with an `entrypoint()` function that returns `{"mAP50": ...}`.

**IMPORTANT:** Write the solution, then immediately run `python3 evaluate.py output/sol01.py` to get the actual score. Do not batch-write multiple solutions — write one, evaluate one, record the score.