# fitness: TBD
"""
Track B radical exploration — copy_paste=0.55 stability mapping.

Model: yolo11n-seg.pt from COCO (nano is faster, allows more iterations)
Epochs: 20 (PROXY_EPOCHS_FINETUNE)
copy_paste=0.55, optimizer='AdamW', lr0=0.01, batch=8, imgsz=640

Goal: Map the copy_paste stability ceiling.
- copy_paste=0.5 is proven safe
- copy_paste=0.65 crashes
- Range 0.55-0.6 is untested

If stable, provides better rare-class oversampling (15x Leaf Spot vs Anthracnose imbalance).
"""
from helpers.core import DATA_V1, RUN_DIR, PROXY_EPOCHS_FINETUNE, train_and_eval

def entrypoint():
    return train_and_eval(
        model_path="yolo11n-seg.pt",
        data_yaml=DATA_V1,
        run_dir=RUN_DIR,
        epochs=PROXY_EPOCHS_FINETUNE,
        imgsz=640,
        batch=8,
        copy_paste=0.55,
        optimizer='AdamW',
        lr0=0.01,
        device=0,
        seed=0,
        cleanup=True,
    )