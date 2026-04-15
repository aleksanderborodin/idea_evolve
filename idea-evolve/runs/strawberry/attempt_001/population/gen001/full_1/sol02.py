"""
Full agent — attempt 2: More epochs + slightly higher copy_paste.

Strategy: Fine-tune from WEIGHTS_EXP5 for 40 epochs with copy_paste=0.6
to better address the 15x class imbalance (Anthracnose is rarest).
More epochs should close the gap from our 20-epoch proxy to the 100-epoch baseline.

Expected: ~0.85-0.90 mAP50 (proxy for 100-epoch performance)
"""
from helpers.core import train_and_eval, WEIGHTS_EXP5, PROXY_EPOCHS_EXTENDED


def entrypoint():
    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=PROXY_EPOCHS_EXTENDED,
        copy_paste=0.6,
        lr0=0.001,
        tta=True,
    )