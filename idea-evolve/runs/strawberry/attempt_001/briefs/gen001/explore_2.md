## Current Population Status
Best solution: None yet — this is generation 1. Prior experiments showed copy_paste=0.5 was the single best augmentation (exp5 val mAP50=0.945 vs baseline 0.935). The copy_paste parameter space has only been partially explored (tested 0.3 and 0.5).

## Read first
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/description.md
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/helpers/core.py
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/initial_ideas.md

## Directive

This is a **Track A exploitation** — refine the best known approach with parameter exploration.

**Primary direction:** Explore copy_paste parameter space beyond {0.3, 0.5}. Try:
- `copy_paste=0.6` or `copy_paste=0.7` — higher values
- `copy_paste_mode="mixup"` vs default `"flip"` — different pasting strategy

**Starting point:** WEIGHTS_EXP5 (100-epoch trained, copy_paste=0.5). Fine-tune for 20 epochs.

**Methodology:**
1. Test `copy_paste=0.65` with 20 epoch fine-tune (PROXY_EPOCHS_FINETUNE=20)
2. If that shows promise (>0.90 mAP50), optionally test `copy_paste=0.7` or `copy_paste_mode="mixup"`
3. Use `train_and_eval()` helper from helpers.core

**Constraints:**
- Do NOT revisit `lr0` tuning — exp3 already found the optimal range [0.003, 0.01]
- Do NOT test yolo11s — explore_1 is testing model scale separately
- Keep flipud=0.0 — exp4 proved vertical flips hurt
- Use the venv Python: `/home/sasha/Desktop/idea_evolve/first_project/venv/bin/python`

**Output:** Write solution(s) to `output/sol01.py` (and sol02.py if testing a second variant). Run evaluate.py on each. Record all scores.