"""
Baseline: fine-tune from exp5 (best known) for 20 epochs with standard defaults.

Starting from the exp5 checkpoint (copy_paste=0.5, 100-epoch trained, val mAP50=0.945)
and continuing training with its original hyperparameters establishes the "zero delta"
baseline for fine-tuning experiments.

Expected proxy score: approximately equal to or slightly above exp5's val mAP50.
"""


def entrypoint():
    import os
    import shutil
    os.environ["CLEARML_SDK_ENABLED"] = "0"

    from helpers.core import (
        train_and_eval, WEIGHTS_EXP5, PROXY_EPOCHS_FINETUNE,
    )

    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=PROXY_EPOCHS_FINETUNE,
        lr0=0.001,          # lower LR for fine-tuning (original was 0.01)
        copy_paste=0.5,     # same as exp5 — maintain the class-balance aug
        copy_paste_mode="flip",
    )
