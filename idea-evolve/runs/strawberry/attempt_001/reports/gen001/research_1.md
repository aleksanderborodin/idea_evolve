# Research Agent Debrief — gen001 research_1

## What did you try?

**Literature survey (primary work):**
- Searched arXiv for: class imbalance segmentation, boundary-aware losses, agricultural disease segmentation
- Fetched and analyzed abstracts from 15+ relevant papers
- Deep-read 6 papers in detail: 2603.26755, 2407.01517, 2503.00242, 2601.11645, 2510.24202, 2504.06389

**Findings produced (output/report.md):**
1. BCE-Dice-Lovász composite loss + inverse-frequency class weighting (most actionable, YOLO26-backed)
2. Domain-guided copy-paste with spatial constraints (builds on copy_paste=0.5 baseline)
3. Tversky+Focal loss hybrid for severe class imbalance
4. Progressive resolution training (320→640)
5. Boundary-aware loss terms (cbDice/BEL)
6. "NOT worth trying" list: DETR, SAM, VLM-based SSDA, pseudo-labeling

No solutions were written — this was a pure research mission.

---

## What information did you lack?

1. **Per-class mAP50 breakdown of the current best solution (exp5)**. The description.md gives val mAP50=0.945 overall but no per-class numbers. I cannot estimate how much Anthracnose (89 instances) and Blossom Blight drag down the average. This is critical for deciding whether loss engineering should target specific rare classes or the overall distribution.

2. **YOLO11's internal loss computation API** — paper 2603.26755 monkey-patches YOLO26. I don't know if YOLO11 exposes the same hook points for custom loss injection. Without a tested code snippet, agents will spend turns discovering the API.

3. **Per-class lesion pixel area / size distribution** — Progressive resolution training helps more for small lesions. I don't know if Anthracnose lesions are typically 5px or 200px on average.

4. **Validation set composition** — How many instances per class on the val split? This matters for estimating whether inverse-frequency weighting during training actually balances the val performance.

---

## What given facts might be wrong or outdated?

1. **exp2 "own data hurt"** — The description.md says adding 49 self-collected images hurt (exp2). But it doesn't explain *why* — likely due to annotation quality issues or distribution mismatch. This is an important clue: more data ≠ better data. Any new data collection should be vetted for annotation consistency before use. But I cannot verify this without the actual self-collected images and their per-class stats.

2. **copy_paste convergence lag** — "copy_paste lags behind at epoch 20-40 but overtakes at epoch 50+" is noted for from-scratch training. This is presented as a caution, but it doesn't affect our fine-tuning setup (WEIGHTS_EXP5 is already converged at 100 epochs). The caution is irrelevant for the default Mode 1 (fine-tune from exp5) but may matter for Mode 2 (from-scratch with 50 epochs).

3. **Model size claim** — description.md mentions `yolo11s-seg.pt (3.5× more params)` as "might capture subtler disease features." This is untested. The small model may actually generalize better given our small dataset (1450 training images). Larger model = more overfitting risk.

---

## Was the State of Affairs accurate?

**Accurate:** The State of Affairs correctly says "no solutions have been evaluated yet" for gen 0 and that initial ideas are seeded from user-provided facts. This matches the cold-start situation.

**Incomplete/Missing:** It contains no strategic leads, no per-experiment analysis, no identified gaps. This is expected for gen 0 but means agents in gen 1 must reconstruct context from description.md and papers rather than having pre-digested strategic leads. The brief was adequate for a research agent starting from scratch.

---

## What would you do differently with more or different context?

1. **With per-class mAP50 for exp5**: I would refine Finding 1 (which classes to upweight) and could estimate realistic improvement bounds. For instance, if Anthracnose mAP50 is 0.3 vs Leaf Spot at 0.98, there's 0.6+ mAP50 headroom on that class alone.

2. **With a working YOLO11 loss-injection code snippet**: I would provide a tested implementation of the BCE-Dice-Lovász loss in the findings itself, not just a conceptual description. Agents would save 2-3 turns of API exploration.

3. **With the per-class instance counts for val split**: I would be more precise about which classes benefit most from progressive resolution and which are boundary-sensitive.

4. **With the actual training curves for exp5 and exp6** (the results.csv files): I would analyze whether the model plateaus on certain classes after epoch 20 — informing whether 40-epoch extended fine-tuning is warranted.

---

## Specific experiments to run?

1. **Loss function ablation** — Run 3 identical fine-tune configs (copy_paste=0.5, 20 epochs, same seed) with different loss functions:
   - Control: default YOLO loss
   - Treatment A: BCE-Dice-Lovász composite + inverse-frequency weights
   - Treatment B: Tversky+Focal (α=0.3, β=0.7)
   Compare per-class mAP50 breakdown. This is the single most valuable experiment.

2. **Per-class baseline** — Before any loss engineering, run `evaluate_on_test()` on WEIGHTS_EXP5 to get per-class mAP50/P/R. This is the prerequisite for all other experiments. Store in LAST_PER_CLASS_METRICS so it's accessible.

3. **Domain-guided copy-paste vs standard copy-paste** — Same as exp5 but with domain-guided constraint. Test whether spatial Plausibility improves minority class mAP50 without hurting majority classes.

4. **Progressive resolution** — 10 epochs at 320px + 10 at 640px vs 20 epochs at 640px. Measure per-class delta to see which diseases benefit.

---

## What surprised you?

1. **No agricultural disease segmentation papers found** — Searching for "strawberry disease segmentation YOLO" returned zero results on arXiv. This is a genuinely under-researched niche. The closest relevant work is in medical imaging (fetal head, surgical instruments, retinal vessels). Transferability is reasonable but requires adaptation.

2. **YOLO26 is already here** — Paper 2603.26755 uses YOLO26-Seg (not YOLO11). Ultralytics has moved to a newer version. If YOLO26-seg.pt is available in the ultralytics package, it might be worth trying as a drop-in replacement. The custom loss approach they demonstrate on YOLO26 may apply to YOLO11 as well.

3. **Boundary losses are well-studied** — Multiple papers independently converge on the same pattern: combine Dice (region) with boundary-aware terms. This is a robust finding across medical imaging. The challenge is that YOLO doesn't expose the segmentation head's loss computation directly — requires monkey-patching.

4. **copy_paste=0.5 is the confirmed winner** — The description.md correctly identifies this as the best experiment. No prior work tried copy-paste with domain guidance, different loss functions, or class-weighted sampling. These are genuinely unexplored directions.

---

## Helper tools feedback

I did not use helpers directly (this was a research-only mission). However, I read the helpers/README.md and core.py descriptions.

**Useful:** `train_and_eval` and `evaluate_on_test` are well-documented and cover the Mode 1 (fine-tune) and evaluation use cases well. The explicit note about `optimizer='auto'` silently ignoring `lr0` (REC-1) is valuable — this is a real footgun that agents would hit.

**Missing information:** The helpers don't document how to access per-class metrics after evaluation in a machine-readable form. The description.md says `LAST_PER_CLASS_METRICS` is written but I didn't see a helper function to read it back. Agents must use Bash to read the JSON. A `read_last_per_class_metrics()` function would be convenient.

**What helper would have saved significant time:** A `get_per_class_metrics()` helper that reads the most recent evaluation's per-class breakdown from LAST_PER_CLASS_METRICS, returning a structured dict. This would let a research agent do `python3 -c "from helpers.core import get_per_class_metrics; print(get_per_class_metrics())"` without needing to know the file path or JSON structure.

---

## Time budget

**Time was sufficient** for the primary research task (literature survey + findings synthesis). I spent ~15 minutes on web searches and paper analysis, ~5 minutes writing the report.

**With more time, I would have:**
1. Downloaded the full PDFs of papers 2603.26755 and 2601.11645 to read the implementation details (loss formulas, hyperparameter values)
2. Attempted a prototype implementation of the BCE-Dice-Lovász loss to confirm YOLO11 compatibility
3. Checked whether YOLO26-seg.pt is available in the current ultralytics installation
4. Looked at the actual per-class results.csv files from exp5 to understand convergence patterns
