# fitness: 0.5453
"""
Explore Agent — Generation 2 — Track B radical exploration

Primary hypothesis: The val-test gap (val=0.91, test=0.8137) is caused by
small lesions at 640px resolution. Test images may contain smaller or
differently presented disease lesions that are poorly captured at 640px.

Approach: imgsz=832 with yolo11s from exp5 checkpoint.
Higher resolution provides more pixel detail per lesion to capture subtle disease features.

Key changes from gen 1 best (0.8328):
- imgsz=832 instead of 640 (core experimental variable)
- Start from exp5 domain-adapted checkpoint (converged strawberry features)
- Use yolo11s model scale (larger than nano)
- optimizer='AdamW' explicit (avoid auto-optimizer bug)
- copy_paste=0.5 (stable)
- batch=8 (reduced for larger images)
"""
from helpers.core import train_and_eval, WEIGHTS_EXP5, PROXY_EPOCHS_FINETUNE

def entrypoint():
    result = train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=PROXY_EPOCHS_FINETUNE,
        imgsz=832,
        batch=8,
        lr0=0.001,
        copy_paste=0.5,
        optimizer='AdamW',
    )
    return result