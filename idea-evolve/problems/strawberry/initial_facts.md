# Initial Facts — Strawberry Disease Segmentation

## Dataset facts

- Open test split: 743 images, fixed, never used in training (this is the fitness metric source)
- Train split: 1450 images (v1), 1499 images (v2 with self-collected)
- Val split: 307 images (same for v1 and v2 — v2 added images only to train)
- Class imbalance: ~15x between Leaf Spot (most common) and Anthracnose Fruit Rot (rarest)
- All images are RGB, typical resolution 640×640 or similar before YOLO preprocessing
- Disease labels are polygon masks (instance segmentation, not bounding boxes)

## Hardware facts

- GPU: NVIDIA RTX 5060 Ti (Blackwell architecture), 16 GB VRAM
- CUDA: 12.8 (cu128 builds required for RTX 50-series compatibility)
- Training speed: yolo11n-seg at batch=16 runs ~10-11 seconds per epoch
- 50 proxy epochs: ~8-9 minutes wall-clock time
- **Only 1 GPU — all training jobs must be sequential, never parallel**

## Evaluation facts

- Fitness = mask mAP50 on open test split (seg.map50, not box.mAP50)
- Evaluated with `eval_model.val(data=open_v1_yaml, split='test')`
- `best.pt` (best validation epoch during training) is used for test evaluation, not `last.pt`
- ClearML is disabled during idea-evolve runs (env var `CLEARML_SDK_ENABLED=0`)
- Results are cached by SHA-256 of solution file — identical solutions return instantly

## Proxy calibration facts (50-epoch test mAP50 vs 100-epoch val mAP50)

| Config | 50-ep val mAP50 | 100-ep val mAP50 |
|--------|----------------|----------------|
| baseline (exp1) | ~0.847 | 0.935 |
| copy_paste=0.5 (exp5) | ~0.868 | 0.945 |
| combined aug (exp6) | ~0.855 | 0.936 |
| no aug (exp8) | ~0.769 | 0.834 |

Note: proxy (50-ep) values are val mAP50; actual evaluate.py reports test mAP50 which may differ slightly.

## Library versions

- Ultralytics: 8.4
- PyTorch: 2.11 + cu128
- Python: 3.12
- YOLO venv: `/home/sasha/Desktop/idea_evolve/first_project/venv/bin/python`

## Key paths

- Open v1 dataset YAML: `/home/sasha/Desktop/first_project/configs/open_v1.yaml`
- Merged v2 dataset YAML: `/home/sasha/Desktop/first_project/data/merged/dataset.yaml`
- Model weights dir: `/home/sasha/Desktop/first_project/` (yolo11n-seg.pt, yolo26n.pt)
- Experiment training results: `/home/sasha/Desktop/idea_evolve/first_project/runs/segment/runs/strawberry-disease/`
- Best trained weights (exp6, 100ep): `/home/sasha/Desktop/idea_evolve/first_project/weights/exp6_combined_aug.pt`
