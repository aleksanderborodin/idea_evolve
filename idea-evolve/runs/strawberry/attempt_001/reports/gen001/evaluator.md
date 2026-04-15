# Evaluator Report — Generation 1

## strategic_shift: false

Generation 1 established a baseline for the strawberry disease segmentation problem. While no revolutionary new techniques emerged, several important findings were recorded that will shape future generations.

---

## Step 1: Collected Verified Scores

| Solution | Agent | mAP50 | is_valid | eval_time_s |
|----------|-------|-------|----------|-------------|
| explore_1/sol01.py | explore_1 | 0.8328 | 1 | 407.2 |
| explore_2/sol01.py | explore_2 | 0.0000 | 0 | — (broken pipe) |
| full_1/sol01.py | full_1 | 0.8137 | 1 | 244.5 |

Gen-0 baseline reference: sol01=0.8137, sol02=0.8175.

**Best valid score this generation: 0.8328 (explore_1, yolo11s from COCO)**

---

## Step 2: Key Observations

### yolo11s from COCO outperforms nano baseline at 20 epochs
The most surprising result: training yolo11s-seg.pt (10.1M params) from COCO pretrained weights for 20 epochs achieved 0.8328, beating the nano model (2.9M params) at the same epoch count (0.8137-0.8175). The larger model has more capacity to absorb the strawberry domain in limited training time. This contradicts the assumption that larger models would overfit or underperform in the short fine-tuning regime.

### 20-epoch fine-tune from exp5 is neutral
full_1 attempted to fine-tune from the exp5 converged checkpoint (copy_paste=0.5, 100 epochs) for 20 more epochs with lr0=0.005. The result (0.8137) matched gen_0 baseline exactly. The val-test gap was dramatic: val mAP50=0.91 at epoch 20, test mAP50=0.8137 — a 0.10 gap. Either 20 epochs is too short for positive transfer, or the model is adapting to val distribution without generalizing to test.

### optimizer=auto silently ignores lr0
full_1 explicitly set lr0=0.005 but YOLO logged "ignoring lr0=0.005, optimizer=auto determining best lr0 automatically" and used lr=0.000909. The solution's intended lr0 experiment was completely compromised. All future experiments must pass optimizer='AdamW' explicitly to control lr0.

### copy_paste=0.65 crashes
explore_2's only solution crashed with `[Errno 32] Broken pipe` during training/evaluation. Whether this is specifically caused by copy_paste=0.65 or was a random crash is unknown — there are no training logs to diagnose. Safe upper bound appears to be below 0.6.

### TTA, progressive resizing, imgsz=832 are completely unexplored
The research agent identified 6 untested techniques. Not a single one was implemented by any solution agent. The search space remains vast — this is gen 1 and the frontier is essentially at the starting line.

---

## Step 3: Ideas Created

Eight new idea files:
- idea_001: yolo11s fine-tune from exp5 checkpoint
- idea_002: imgsz=832 higher resolution
- idea_003: TTA at evaluation (native, zero-cost)
- idea_004: copy_paste > 0.5 causes instability
- idea_005: optimizer=auto ignores explicit lr0
- idea_006: progressive resolution fine-tuning
- idea_007: val-test distribution gap
- idea_008: explicit optimizer override (AdamW)

---

## Step 4: Clusters Updated

Three clusters:
- cluster_001: Model scale and resolution (best: 0.8328)
- cluster_002: Evaluation-time techniques (no valid scores yet)
- cluster_003: Training dynamics and reliability (best: 0.8137)

---

## Step 5: Solution-Idea Map

| Solution | Central | Peripheral | Score |
|----------|---------|-----------|-------|
| sol_001 (full_1) | idea_008 (intended but bug prevented) | copy_paste=0.5 | 0.8137 |
| sol_002 (explore_1) | idea_001 (yolo11s from COCO) | copy_paste=0.5 | 0.8328 |
| sol_003 (explore_2) | idea_004 (failed — invalid) | — | 0.0 |

---

## Step 6: Coverage Matrix

Only 4 idea combinations have been tried, most ideas have zero coverage. The coverage matrix reveals a vast unexplored space:
- TTA: 0 tries (easiest win — just augment=True)
- imgsz=832: 0 tries
- yolo11s from exp5: 0 tries (only from COCO)
- progressive resizing: 0 tries
- class weighting: 0 tries
- label smoothing: 0 tries
- NMS tuning: 0 tries

---

## Debrief

### What did I try?
I evaluated 3 solutions from gen_1: yolo11s from COCO (0.8328), exp5 fine-tune with lr0=0.005 (0.8137), and copy_paste=0.65 (invalid, broken pipe). I created 8 ideas, 3 patterns, 3 clusters, and documented all findings.

### What information did I lack?
1. No per-class mAP — I cannot tell which disease classes are the bottleneck
2. No test image visibility — cannot diagnose failure modes visually
3. No training logs from explore_2's crash — cannot determine if copy_paste=0.65 specifically caused it
4. No direct exp5→test zero-shot baseline — don't know if 20-epoch fine-tune is better than no fine-tune

### Was the State of Affairs accurate?
Yes — gen 0 had no knowledge and everything was correctly marked as open. The initial facts and ideas from the problem files were accurate.

### What would I do differently?
1. Apply TTA to the best model FIRST — it's free and would give a more accurate fitness signal for all comparisons
2. Test yolo11s from exp5 checkpoint (not from COCO) since that was the one positive finding
3. Explicitly use optimizer='AdamW' in every training call to avoid the auto-optimizer trap
4. Start with imgsz=832 as the primary exploration direction since small lesions are clearly a limiting factor

### Specific experiments to run?
1. **TTA on exp5 best.pt**: model.val(augment=True) — no retraining, pure evaluation improvement
2. **yolo11s from exp5 + AdamW + lr0=0.001, 20 epochs**: combine best model with best starting point
3. **imgsz=832 + copy_paste=0.5 + optimizer=AdamW**: test higher resolution hypothesis
4. **copy_paste=0.55 and 0.6** to find the actual stability boundary (instead of jumping to 0.65)

### What surprised me?
The yolo11s from COCO beating nano from COCO by 0.015 at the same epoch count was unexpected — I would have predicted the larger model would need more epochs to show its value. The complete absence of TTA usage despite being a native YOLO feature was also surprising.

### Helper tools feedback?
The train_and_eval() function is clean and correct, but it passes optimizer='auto' which silently overrides explicit lr0. The docstring should explicitly warn about this or default to a non-auto optimizer. The RUN_DIR cleanup works correctly.

### Time budget?
I completed all evaluation work in the allocated session. No time pressure issues. If I had more time, I would have manually applied TTA to the explore_1 solution to see if it pushes above 0.84.
