# fitness: TBD
"""
Full Agent — Generation 2 — Track B radical exploration

Question: Is yolo11s at 20 epochs from COCO (0.8328) just lucky noise,
or does the larger model genuinely outperform nano?

This run gives yolo11s from COCO a proper 50-epoch training (PROXY_EPOCHS_SCRATCH)
to see if it converges to a higher score than nano at the same epoch budget.

Key variables:
- model: yolo11s-seg.pt (COCO pretrained) — the KEY variable being tested
- epochs: 50 (PROXY_EPOCHS_SCRATCH) — full convergence from COCO
- imgsz: 640 (standard)
- copy_paste: 0.5 (proven best augmentation)
- optimizer: AdamW (explicit, not auto)
- lr0: 0.01 (higher lr for from-scratch training)
- batch: 8 (yolo11s is larger, needs more memory)

What to preserve: copy_paste=0.5, AdamW optimizer
What NOT to revisit: fine-tuning from exp5 (that's for exploit agents)
"""
from helpers.core import DATA_V1, RUN_DIR, PROXY_EPOCHS_SCRATCH, train_and_eval

def entrypoint():
    return train_and_eval(
        model_path="yolo11s-seg.pt",
        data_yaml=DATA_V1,
        run_dir=RUN_DIR,
        epochs=PROXY_EPOCHS_SCRATCH,   # 50 epochs — full convergence from COCO
        imgsz=640,
        batch=8,
        copy_paste=0.5,
        optimizer='AdamW',
        lr0=0.01,
        device=0,
        seed=0,
        cleanup=True,
    )