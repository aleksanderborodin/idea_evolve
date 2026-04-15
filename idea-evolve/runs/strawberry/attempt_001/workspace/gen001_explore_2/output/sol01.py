# fitness: TBD
from helpers.core import train_and_eval

def entrypoint():
    return train_and_eval(
        model_path="/home/sasha/Desktop/first_project/yolo11s-seg.pt",
        epochs=50,
        lr0=0.01,
        copy_paste=0.5,
        optimizer="AdamW",
        imgsz=640,
        batch=16,
        seed=0,
    )