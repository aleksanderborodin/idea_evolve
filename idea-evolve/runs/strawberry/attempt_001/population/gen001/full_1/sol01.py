"""
Full agent baseline — reproduce exp5 with TTA + label_smoothing.

Strategy: Fine-tune from WEIGHTS_EXP5 (best.pt from exp5 with copy_paste=0.5)
for 20 epochs using the same copy_paste=0.5. Add TTA at eval and light
label_smoothing=0.05 for slight regularization.

Expected: ~0.92-0.94 mAP50 (proxy for 100-epoch performance ~0.945)
"""
from helpers.core import train_and_eval, WEIGHTS_EXP5, PROXY_EPOCHS_FINETUNE


def entrypoint():
    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=PROXY_EPOCHS_FINETUNE,
        copy_paste=0.5,
        lr0=0.001,
        label_smoothing=0.05,
        tta=True,
    )