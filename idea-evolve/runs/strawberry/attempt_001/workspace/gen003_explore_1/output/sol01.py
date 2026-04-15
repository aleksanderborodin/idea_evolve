# fitness: TBD
"""
Explore Agent — Generation 3 — Track B radical exploration

Primary experiment: Progressive resizing 640→832

Direct imgsz=832 fine-tuning from a 640-converged checkpoint was catastrophic
(gen2 explore_1: 0.5453 regression). But progressive resizing — train at 640
for 20 epochs, then fine-tune at 832 for 10 epochs — may preserve domain
adaptation while capturing higher-resolution disease features.

Stage 1: Train yolo11s-seg.pt from COCO at 640 for 20 epochs with
copy_paste=0.5, optimizer='AdamW', lr0=0.01, batch=8

Stage 2: Load best.pt from stage 1, fine-tune at 832 for 10 epochs with
lr0=0.001 (lower lr for fine-tuning), copy_paste=0.5, batch=8

Fallback: If stage 2 fails, evaluate stage 1's best.pt at 640.
"""
from helpers.core import DATA_V1, RUN_DIR, PROXY_EPOCHS_FINETUNE, train_and_eval
from pathlib import Path

def entrypoint():
    run_dir_stage1 = Path("/tmp/idea_evolve_strawberry/run_stage1")
    run_dir_stage2 = Path("/tmp/idea_evolve_strawberry/run_stage2")

    print("=" * 60)
    print("STAGE 1: Train yolo11s at 640 for 20 epochs")
    print("=" * 60)

    result_stage1 = train_and_eval(
        model_path="yolo11s-seg.pt",
        data_yaml=DATA_V1,
        run_dir=run_dir_stage1,
        epochs=20,
        imgsz=640,
        batch=8,
        copy_paste=0.5,
        optimizer='AdamW',
        lr0=0.01,
        device=0,
        seed=0,
        cleanup=True,
    )
    print(f"Stage 1 result: mAP50={result_stage1['mAP50']:.4f}")

    best_pt_stage1 = run_dir_stage1 / "weights" / "best.pt"
    if not best_pt_stage1.exists():
        best_pt_stage1 = run_dir_stage1 / "weights" / "last.pt"

    print(f"Stage 1 checkpoint: {best_pt_stage1}")

    print("=" * 60)
    print("STAGE 2: Fine-tune stage1 checkpoint at 832 for 10 epochs")
    print("=" * 60)

    try:
        result_stage2 = train_and_eval(
            model_path=str(best_pt_stage1),
            data_yaml=DATA_V1,
            run_dir=run_dir_stage2,
            epochs=10,
            imgsz=832,
            batch=8,
            copy_paste=0.5,
            optimizer='AdamW',
            lr0=0.001,
            device=0,
            seed=0,
            cleanup=True,
        )
        print(f"Stage 2 result: mAP50={result_stage2['mAP50']:.4f}")
        return result_stage2

    except Exception as e:
        print(f"Stage 2 failed: {e}")
        print("FALLBACK: Evaluating stage 1 checkpoint at 640")

        from helpers.core import evaluate_on_test
        fallback = evaluate_on_test(str(best_pt_stage1), imgsz=640, device=0, tta=False)
        print(f"Fallback result (stage1 @ 640): mAP50={fallback['mAP50']:.4f}")

        fallback["train_time_s"] = result_stage1["train_time_s"]
        fallback["stage1_mAP50"] = result_stage1["mAP50"]
        fallback["stage2_failed"] = True
        fallback["fallback_note"] = "Stage2 failed, returned stage1 evaluated at 640"
        return fallback