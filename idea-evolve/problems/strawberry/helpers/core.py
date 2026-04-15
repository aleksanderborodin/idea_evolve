"""
Core helpers for the Strawberry Disease Segmentation problem.

Import as:
    from helpers.core import WEIGHTS_EXP5, DATA_V1, RUN_DIR, PROXY_EPOCHS_FINETUNE
    from helpers.core import evaluate_on_test, train_and_eval

Agent-readable artifacts (paths listed at bottom of this module):
    TRAIN_LOG_DIR          — YOLO training logs + results.csv per run, preserved on crash
    LAST_PER_CLASS_METRICS — JSON of the most recent per-class test metrics (REC-2)

Agents can open/read these paths via Bash/Read — they live on disk, not in prompt context.
"""
from pathlib import Path

# ── Epoch budgets ──────────────────────────────────────────────────────────────

PROXY_EPOCHS_FINETUNE  = 20   # Fine-tuning quick exploration (~3.6 min) — default
PROXY_EPOCHS_EXTENDED  = 40   # Fine-tuning for promising configs (~7.2 min) — use when needed
PROXY_EPOCHS_SCRATCH   = 50   # Training from COCO base weights from scratch (~9 min)

# ── Absolute paths ─────────────────────────────────────────────────────────────

# Starting model weights (checkpoints already trained 100 epochs on strawberry)
WEIGHTS_EXP5 = "/home/sasha/Desktop/idea_evolve/first_project/runs/segment/runs/strawberry-disease/exp5_copy_paste/weights/best.pt"
WEIGHTS_EXP6 = "/home/sasha/Desktop/idea_evolve/first_project/weights/exp6_combined_aug.pt"
WEIGHTS_BASE = "/home/sasha/Desktop/first_project/yolo11n-seg.pt"  # COCO pretrained

# Dataset YAMLs
DATA_V1 = "/home/sasha/Desktop/first_project/configs/open_v1.yaml"   # 1450/307/743
DATA_V2 = "/home/sasha/Desktop/first_project/data/merged/dataset.yaml"  # 1499/307/743

# Training output directory (use as temp dir; evaluate.py cleans it up after each run)
RUN_DIR = Path("/tmp/idea_evolve_strawberry/run")

# Preserved training artifacts (survive cleanup — agents can read them later).
# Populated by train_and_eval() on every call: last run's train.log, results.csv,
# args.yaml, and a crash_tail.log if training failed.
TRAIN_LOG_DIR = Path("/tmp/idea_evolve_strawberry/last_train_logs")

# Most recent test-eval per-class breakdown (JSON). Rewritten on every evaluate_on_test.
LAST_PER_CLASS_METRICS = Path("/tmp/idea_evolve_strawberry/last_per_class.json")

# ── Dataset statistics ─────────────────────────────────────────────────────────

DATASET_STATS = {
    "n_train_v1": 1450,
    "n_val": 307,
    "n_test": 743,           # fixed held-out test split — never used in training
    "n_classes": 7,
    "classes": {
        0: "Angular Leafspot",
        1: "Anthracnose Fruit Rot",
        2: "Blossom Blight",
        3: "Gray Mold",
        4: "Leaf Spot",
        5: "Powdery Mildew Fruit",
        6: "Powdery Mildew Leaf",
    },
    # Class imbalance: ~15x between dominant (Leaf Spot) and rarest (Anthracnose)
    "imbalance_ratio": 15.0,
    "dominant_class": "Leaf Spot",
    "rarest_class": "Anthracnose Fruit Rot",
}
CLASS_NAMES = [DATASET_STATS["classes"][i] for i in range(DATASET_STATS["n_classes"])]

# Prior experiment results (100-epoch val mAP50, yolo11n-seg, open v1 dataset)
EXPERIMENT_RESULTS = {
    "exp8_no_aug":       {"val_mAP50_100ep": 0.834, "finding": "aug essential"},
    "exp4_flips":        {"val_mAP50_100ep": 0.921, "finding": "flipud hurts"},
    "exp2_plus_own":     {"val_mAP50_100ep": 0.925, "finding": "own data hurt"},
    "exp3_best_full":    {"val_mAP50_100ep": 0.929, "finding": "lr0=0.005 modest gain"},
    "exp7_final":        {"val_mAP50_100ep": 0.929, "finding": "too many augs"},
    "exp1_baseline":     {"val_mAP50_100ep": 0.935, "finding": "solid YOLO defaults"},
    "exp6_combined_aug": {"val_mAP50_100ep": 0.936, "finding": "copy_paste=0.3 + hsv + perspective + mixup"},
    "exp5_copy_paste":   {"val_mAP50_100ep": 0.945, "finding": "BEST: copy_paste=0.5 addresses imbalance"},
}

# ── Utility functions ──────────────────────────────────────────────────────────

def evaluate_on_test(
    weights_path: str,
    imgsz: int = 640,
    device: int = 0,
    tta: bool = False,
    save_per_class: bool = True,
) -> dict:
    """Evaluate a trained model on the fixed open test split (743 images).

    Returns dict with aggregate metrics plus a `per_class` block:
        {
            "mAP50": float, "mAP50_95": float, "F1": float,
            "precision": float, "recall": float,
            "per_class": {
                "names":      ["Angular Leafspot", ...],   # len=7
                "mAP50":      [...],                       # one entry per class
                "mAP50_95":   [...],
                "precision":  [...],
                "recall":     [...],
            }
        }

    If `tta=True`, runs YOLO's built-in test-time augmentation (`augment=True`),
    which typically adds ~0.5-2% mAP50 at no training cost.

    If `save_per_class=True` (default), writes the per-class block to
    LAST_PER_CLASS_METRICS as JSON so agents can inspect it via Bash/Read
    without re-running eval.

    Usage:
        from helpers.core import evaluate_on_test, WEIGHTS_EXP5
        metrics = evaluate_on_test(WEIGHTS_EXP5, tta=True)
        print(f"mAP50: {metrics['mAP50']:.4f}")
        for name, ap in zip(metrics['per_class']['names'],
                            metrics['per_class']['mAP50']):
            print(f"  {name}: {ap:.4f}")
    """
    import json
    import os
    os.environ.setdefault("CLEARML_SDK_ENABLED", "0")
    from ultralytics import YOLO

    model = YOLO(str(weights_path))
    m = model.val(
        data=DATA_V1,
        split="test",
        imgsz=imgsz,
        device=device,
        augment=tta,
        verbose=False,
        plots=False,
    )
    seg = m.seg
    mp = float(seg.mp)
    mr = float(seg.mr)

    # YOLO v8+ per-class arrays. Guard against missing attributes across versions.
    per_class = {
        "names": list(CLASS_NAMES),
        "mAP50":     _as_list(getattr(seg, "ap50", None)),
        "mAP50_95":  _as_list(getattr(seg, "ap",   None)),
        "precision": _as_list(getattr(seg, "p",    None)),
        "recall":    _as_list(getattr(seg, "r",    None)),
    }

    result = {
        "mAP50":     round(float(seg.map50), 4),
        "mAP50_95":  round(float(seg.map),   4),
        "F1":        round(2 * mp * mr / (mp + mr + 1e-9), 4),
        "precision": round(mp, 4),
        "recall":    round(mr, 4),
        "tta":       bool(tta),
        "per_class": per_class,
    }

    if save_per_class:
        try:
            LAST_PER_CLASS_METRICS.parent.mkdir(parents=True, exist_ok=True)
            LAST_PER_CLASS_METRICS.write_text(json.dumps(result, indent=2))
        except Exception:
            pass

    return result


def _as_list(x):
    """Coerce YOLO metric arrays/tensors/None to a plain float list, rounded to 4dp."""
    if x is None:
        return []
    try:
        return [round(float(v), 4) for v in x]
    except Exception:
        try:
            return [round(float(x), 4)]
        except Exception:
            return []


def train_and_eval(
    model_path: str,
    data_yaml: str = None,
    run_dir: "Path | str" = None,
    epochs: int = None,
    imgsz: int = 640,
    batch: int = 16,
    device: int = 0,
    seed: int = 0,
    cleanup: bool = True,
    optimizer: str = "AdamW",
    lr0: float = 0.001,
    tta: bool = False,
    **train_kwargs,
) -> dict:
    """Standard training + test-evaluation loop. Handles boilerplate.

    Returns dict with mAP50, mAP50_95, F1, precision, recall, per_class, tta, eval_time_s.

    IMPORTANT (REC-1): `optimizer` defaults to 'AdamW' (NOT 'auto') so that an
    explicit `lr0` is actually respected. YOLO's `optimizer='auto'` mode IGNORES
    caller-specified lr0/momentum and picks its own values — a silent footgun.
    If you want the auto-picker, pass `optimizer='auto'` explicitly.

    Args:
        model_path:   path to .pt checkpoint to start from
        data_yaml:    dataset YAML (defaults to DATA_V1)
        run_dir:      training output dir (defaults to RUN_DIR)
        epochs:       training epochs (defaults to PROXY_EPOCHS_FINETUNE=20)
        imgsz:        image size (default 640; try 832 for small lesions)
        batch:        batch size (default 16)
        device:       CUDA device id (default 0)
        seed:         RNG seed (default 0, deterministic)
        cleanup:      if True, delete run_dir after eval (keeps disk clean;
                      logs are ALWAYS preserved to TRAIN_LOG_DIR before cleanup)
        optimizer:    'AdamW' (default), 'SGD', 'Adam', or 'auto'.
                      NOTE: 'auto' IGNORES your lr0. Default 'AdamW' respects it.
        lr0:          initial learning rate (default 0.001 for fine-tuning).
                      Only honoured if optimizer != 'auto'.
        tta:          if True, evaluation uses test-time augmentation.
        **train_kwargs: any other YOLO train() kwarg (copy_paste, hsv_h, etc.)

    Example — fine-tune from exp5 with higher copy_paste:
        from helpers.core import train_and_eval, WEIGHTS_EXP5
        return train_and_eval(
            model_path=WEIGHTS_EXP5,
            epochs=20,
            lr0=0.001,
            copy_paste=0.7,
        )

    Example — staged fine-tuning (freeze backbone):
        r1 = train_and_eval(WEIGHTS_EXP5, epochs=10, freeze=10, lr0=0.005, cleanup=False)
        best_pt = Path("/tmp/idea_evolve_strawberry/run/weights/best.pt")
        return train_and_eval(str(best_pt), epochs=10, lr0=0.001)
    """
    import os, shutil, time
    from pathlib import Path as _Path
    os.environ.setdefault("CLEARML_SDK_ENABLED", "0")
    from ultralytics import YOLO

    _data = data_yaml or DATA_V1
    _run = _Path(run_dir) if run_dir else RUN_DIR
    _epochs = epochs or PROXY_EPOCHS_FINETUNE

    if cleanup:
        shutil.rmtree(_run, ignore_errors=True)
    TRAIN_LOG_DIR.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    crashed = False
    crash_msg = ""
    try:
        model = YOLO(str(model_path))
        model.train(
            data=_data,
            epochs=_epochs,
            imgsz=imgsz,
            batch=batch,
            device=device,
            seed=seed,
            deterministic=True,
            project=str(_run.parent),
            name=_run.name,
            exist_ok=True,
            verbose=False,
            plots=False,
            optimizer=optimizer,
            lr0=lr0,
            **train_kwargs,
        )
    except Exception as e:
        crashed = True
        crash_msg = f"{type(e).__name__}: {e}"
    finally:
        _preserve_training_logs(_run, crashed, crash_msg)

    if crashed:
        raise RuntimeError(
            f"Training failed: {crash_msg}. "
            f"Logs preserved at {TRAIN_LOG_DIR} — agents can read them."
        )

    best_pt = _run / "weights" / "best.pt"
    if not best_pt.exists():
        best_pt = _run / "weights" / "last.pt"

    metrics = evaluate_on_test(str(best_pt), imgsz=imgsz, device=device, tta=tta)
    metrics["train_time_s"] = round(time.perf_counter() - t0, 1)

    if cleanup:
        shutil.rmtree(_run, ignore_errors=True)

    return metrics


def _preserve_training_logs(run_path, crashed: bool, crash_msg: str):
    """REC-5: copy training artifacts to TRAIN_LOG_DIR before cleanup.

    What lands there after every run (overwritten each call):
        TRAIN_LOG_DIR/results.csv      — YOLO per-epoch loss + mAP curves
        TRAIN_LOG_DIR/args.yaml        — the exact train() config that ran
        TRAIN_LOG_DIR/train.log        — full stdout/stderr if YOLO wrote one
        TRAIN_LOG_DIR/crash_tail.log   — only on crash: last exception + context
    """
    import shutil, os
    try:
        TRAIN_LOG_DIR.mkdir(parents=True, exist_ok=True)
        # Clear old artifacts to avoid confusing stale + fresh output
        for p in TRAIN_LOG_DIR.iterdir():
            if p.is_file():
                try: p.unlink()
                except Exception: pass
        # Copy whatever YOLO produced
        for fname in ("results.csv", "args.yaml", "train.log", "events.out.tfevents"):
            for src in Path(run_path).rglob(fname):
                try:
                    shutil.copy2(src, TRAIN_LOG_DIR / src.name)
                    break
                except Exception:
                    pass
        if crashed:
            (TRAIN_LOG_DIR / "crash_tail.log").write_text(
                f"Training crashed: {crash_msg}\n"
                f"Run directory (may still exist): {run_path}\n"
            )
    except Exception:
        pass
