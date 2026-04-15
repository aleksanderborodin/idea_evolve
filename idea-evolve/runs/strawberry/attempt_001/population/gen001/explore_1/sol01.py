# fitness: 0.8328
"""
Explore Agent — Generation 1 — Track B radical exploration

Approach: Use yolo11s-seg.pt (small model, 10.1M params) instead of
yolo11n-seg.pt (nano model, 2.9M params) that all prior experiments used.

This is a completely different model scale — 3.5x more parameters —
that has never been tested on this problem.

Training: 20 epochs fine-tuning from COCO-pretrained s-model weights,
with copy_paste=0.5 (proven best augmentation), imgsz=640, batch=8.
"""
from helpers.core import DATA_V1, RUN_DIR, PROXY_EPOCHS_FINETUNE, train_and_eval

def entrypoint():
    return train_and_eval(
        model_path="yolo11s-seg.pt",   # COCO pretrained small model (10.1M params)
        data_yaml=DATA_V1,
        run_dir=RUN_DIR,
        epochs=PROXY_EPOCHS_FINETUNE,   # 20 epochs
        imgsz=640,
        batch=8,                        # s-model needs less batch than n-model
        copy_paste=0.5,                 # proven best from exp5
        device=0,
        seed=0,
        cleanup=True,
    )