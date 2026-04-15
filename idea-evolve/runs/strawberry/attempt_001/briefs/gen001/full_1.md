## Current Population Status
Best solution: None yet — this is generation 1. Prior experiments established:
- copy_paste=0.5 is the best augmentation (exp5, val mAP50=0.945)
- lr0=0.005 is optimal within tested range (exp3, 0.929)
- yolo11n-seg is the standard model (all prior experiments)
- flipud hurts performance, too many augs hurt

## Read first
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/description.md
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/helpers/core.py
- /home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/initial_ideas.md

## Directive

This is a **full solution attempt** — build end-to-end from proven best practices.

**Approach:** Combine the two most validated findings into a strong baseline:
1. Start from WEIGHTS_EXP5 (best known checkpoint, already trained with copy_paste=0.5)
2. Use `copy_paste=0.5` (proven best) + `lr0=0.005` (exp3 best)
3. Fine-tune for 20 epochs (PROXY_EPOCHS_FINETUNE)
4. Keep flipud=0.0 and avoid over-augmentation (exp6 showed combined augs hurt vs single best aug)

This should establish a solid reference point for Track B agents to beat.

**Key code pattern:**
```python
from helpers.core import train_and_eval, WEIGHTS_EXP5

def entrypoint():
    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=20,
        copy_paste=0.5,
        lr0=0.005,
    )
```

**Constraints:**
- Do NOT test yolo11s — that's explore_1's job
- Do NOT increase copy_paste above 0.5 — explore_2 is testing that direction
- Use the venv Python: `/home/sasha/Desktop/idea_evolve/first_project/venv/bin/python`

**Output:** Write solution to `output/sol01.py` with `entrypoint()`. Run evaluate.py. Record mAP50 score.