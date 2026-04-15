# fitness: TBD
from helpers.core import train_and_eval, WEIGHTS_EXP5

def entrypoint():
    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=20,
        copy_paste=0.8,
        lr0=0.002,
        optimizer="AdamW",
        tta=True,
    )