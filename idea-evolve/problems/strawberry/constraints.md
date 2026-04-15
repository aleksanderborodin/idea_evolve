# Strawberry Segmentation — Hard Constraints

## GPU serialization — automatic via file lock

evaluate.py holds a **system-wide exclusive file lock** (`/tmp/idea_evolve_gpu.lock`)
while training. If two agents run evaluate.py simultaneously, the second **blocks and waits**
until the first finishes. You do not need to manage this — it is automatic.

This means:
- `parallel_groups` in the manifest can have any structure
- Two agents in the same group is fine — they will naturally queue at the GPU lock
- No need for sequential `[[a], [b], [c]]` grouping (though it still works)

## Solution requirements

Solutions must:
1. Define `def entrypoint()` that returns a dict containing `"mAP50"` (float, 0–1)
2. Import `ultralytics` **inside** `entrypoint()`, not at module level
   (evaluate.py re-execs into the correct venv before calling entrypoint)
3. Set `os.environ["CLEARML_SDK_ENABLED"] = "0"` before importing ultralytics
4. Use the absolute paths from `helpers.core` (`DATA_V1`, `WEIGHTS_EXP5`, etc.)
5. Keep total training epochs between 20 and 40 per evaluation
   - Use `PROXY_EPOCHS_FINETUNE` (20) for quick exploration — default choice
   - Use `PROXY_EPOCHS_EXTENDED` (40) only when the config is promising and needs more epochs to converge
   - Hard cap: 60 epochs total. Do not exceed this.

Solutions **must not**:
- Leave GPU processes running after returning (training and evaluation must finish)
- Import ultralytics or torch at module level (causes import errors before re-exec)
- Use `resume=True` on the training call (conflicts with the unique run dir)

## Epoch budget

| Constant | Epochs | Wall-clock time | When to use |
|----------|--------|----------------|-------------|
| `PROXY_EPOCHS_FINETUNE` | 20 | ~3.6 min | **Default.** Quick exploration and comparisons |
| `PROXY_EPOCHS_EXTENDED` | 40 | ~7.2 min | Promising config that needs more epochs to converge |
| `PROXY_EPOCHS_SCRATCH` | 50 | ~9 min | Training from COCO weights with no strawberry checkpoint |
| Hard cap | 60 | ~10.8 min | Never exceed this |

**Rule of thumb:** Start with 20. If a technique looks promising but the loss is still dropping at epoch 20, re-run with 40. Multi-stage training counts the sum of all stages toward the budget.

## Absolute data paths

```python
DATA_V1      = "/home/sasha/Desktop/first_project/configs/open_v1.yaml"
DATA_V2      = "/home/sasha/Desktop/first_project/data/merged/dataset.yaml"
WEIGHTS_EXP5 = "/home/sasha/Desktop/idea_evolve/first_project/runs/segment/runs/strawberry-disease/exp5_copy_paste/weights/best.pt"
WEIGHTS_EXP6 = "/home/sasha/Desktop/idea_evolve/first_project/weights/exp6_combined_aug.pt"
WEIGHTS_BASE = "/home/sasha/Desktop/first_project/yolo11n-seg.pt"
RUN_DIR      = Path("/tmp/idea_evolve_strawberry/run")
```

All available as imports from `helpers.core`. Always use these — do not hardcode paths.

## Test evaluation

Always evaluate on the **open test split** using `DATA_V1` yaml with `split="test"`.
This is the fair comparison metric used by all experiments (exp1–exp8).
Evaluation on val split is done automatically during training (for best.pt selection),
but the reported `mAP50` fitness must come from the test split.
