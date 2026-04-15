# fitness: 0.8137
from helpers.core import train_and_eval, WEIGHTS_EXP5

def entrypoint():
    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=20,
        copy_paste=0.5,
        lr0=0.005,
    )