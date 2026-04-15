"""
Stronger copy-paste: fine-tune from exp5 with copy_paste=0.7 and class-targeted HSV.

Since copy_paste=0.5 was the best single change in 8 experiments, the first hypothesis
to test is: can we go higher? Also test class-targeted HSV variation since disease
appearance changes under different lighting conditions.

Explores: copy_paste probability 0.5 → 0.7, mild HSV boost for rare class distinction.
"""


def entrypoint():
    import os
    os.environ["CLEARML_SDK_ENABLED"] = "0"

    from helpers.core import train_and_eval, WEIGHTS_EXP5, PROXY_EPOCHS_FINETUNE

    return train_and_eval(
        model_path=WEIGHTS_EXP5,
        epochs=PROXY_EPOCHS_FINETUNE,
        lr0=0.001,
        copy_paste=0.7,
        copy_paste_mode="flip",
        hsv_h=0.02,        # slight hue shift to improve color-based class distinction
        hsv_s=0.75,
        hsv_v=0.45,
    )
