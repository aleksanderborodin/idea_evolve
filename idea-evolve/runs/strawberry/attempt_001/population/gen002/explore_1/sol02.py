# fitness: TBD
"""
Explore Agent — Generation 2 — Attempt 2

After the imgsz=832 fine-tuning degraded performance (0.5453 vs exp5's 0.7876 at same resolution),
trying yolo11s from COCO at 640 for 40 epochs (from-scratch training, within epoch budget).

This tests whether the s-model scale can achieve better results than nano when
trained from scratch with sufficient epochs.
"""
from helpers.core import train_and_eval, PROXY_EPOCHS_EXTENDED

def entrypoint():
    result = train_and_eval(
        model_path="yolo11s-seg.pt",
        epochs=PROXY_EPOCHS_EXTENDED,
        imgsz=640,
        batch=8,
        lr0=0.01,
        copy_paste=0.5,
        optimizer='AdamW',
    )
    return result