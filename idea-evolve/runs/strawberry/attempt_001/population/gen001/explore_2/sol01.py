# fitness: TBD
# Approach: copy_paste=0.65 (higher than exp5's 0.5) to further oversample rare classes
from helpers.core import WEIGHTS_EXP5, PROXY_EPOCHS_FINETUNE, train_and_eval

def entrypoint():
    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=PROXY_EPOCHS_FINETUNE,
        copy_paste=0.65,
        lr0=0.005,
    )