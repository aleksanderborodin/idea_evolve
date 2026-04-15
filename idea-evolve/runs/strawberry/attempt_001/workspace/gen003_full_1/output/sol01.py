# fitness: TBD
"""
Full Agent — Generation 3 — Track A Directed Exploitation

Question: Does yolo11s from COCO benefit from more than 20 epochs?

Gen 1's best result (0.8328) was yolo11s from COCO at 20 epochs — only 1 data point,
possibly still improving. Gen 2's yolo11s attempts (40ep and 50ep) both timed out
before evaluation.

Strategy: Train yolo11s-seg.pt from COCO pretrained at 40 epochs (PROXY_EPOCHS_EXTENDED).
This tests whether the model was still improving at 20 epochs or had already plateaued.

Expected outcomes:
- If score > 0.8328: model was still improving at 20 epochs → prioritize longer training
- If score ≈ 0.8328: model plateaus around 20 epochs from COCO → explore other directions
- If score < 0.8328: overfitting at 40 epochs → stick with 20 or add regularization

Config: yolo11s-seg.pt (COCO pretrained), 40 epochs, copy_paste=0.5,
optimizer=AdamW (explicit), lr0=0.01, batch=8, imgsz=640.
"""
from helpers.core import PROXY_EPOCHS_EXTENDED, train_and_eval

def entrypoint():
    return train_and_eval(
        model_path="/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/yolo11s-seg.pt",
        data_yaml="/home/sasha/Desktop/first_project/configs/open_v1.yaml",
        run_dir="/tmp/idea_evolve_strawberry/run",
        epochs=PROXY_EPOCHS_EXTENDED,
        imgsz=640,
        batch=8,
        copy_paste=0.5,
        optimizer="AdamW",
        lr0=0.01,
        device=0,
        seed=0,
        cleanup=True,
    )