# Research Agent Debrief — Gen 3 Research 1

## What did you try?

**EXP-3: Per-class mAP50 extraction (COMPLETED — ~90 seconds)**
- Used `evaluate_on_test(WEIGHTS_EXP5)` with `save_per_class=True` on the exp5 zero-shot model
- Extracted mAP50, precision, and recall for all 7 disease classes
- Results: aggregate mAP50=0.8271 on test split
- Per-class breakdown:
  - Angular Leafspot: mAP50=0.7201, P=0.8011, R=0.6943
  - Anthracnose Fruit Rot: mAP50=0.7865, P=0.7384, R=0.7302
  - Blossom Blight: mAP50=0.8503, P=0.7416, R=1.0000
  - Gray Mold: mAP50=0.9289, P=0.8589, R=0.9051
  - Leaf Spot: mAP50=0.7419, P=0.8517, R=0.5711
  - Powdery Mildew Fruit: mAP50=0.8441, P=0.9003, R=0.7008
  - Powdery Mildew Leaf: mAP50=0.9181, P=0.8250, R=0.8776

**EXP-6: TTA validation after fresh training (INTERRUPTED — did not complete)**
- Started training yolo11s from COCO at 20 epochs using `train_and_eval()`
- Timeout occurred during training (~3-6 minutes into the 20-epoch run)
- No TTA comparison results obtained

## What information did you lack?

1. **Confusion matrix data** — I don't know which classes are confused with which. Leaf Spot's low recall (0.5711) could be due to confusion with Gray Mold, or due to small lesion size, or annotation issues. Without the per-class confusion matrix, this is unresolvable.
2. **Instance count per class in test set** — I know train set counts (1365 for Leaf Spot, 89 for Anthracnose) but not how many are in the 743-image test set. This would let me compute weighted vs. unweighted mAP50.
3. **Whether TTA works on fresh training** — EXP-6 was the definitive experiment and it didn't complete.
4. **The `LAST_PER_CLASS_METRICS` JSON path** — The description.md mentions `/tmp/idea_evolve_strawberry/last_per_class.json` but I didn't read this file directly. The per-class data was captured from the inline Python output instead.

## What given facts might be wrong or outdated?

1. **"15x class imbalance is the root cause"** — This is stated as the root cause in description.md and all prior reports. But per-class mAP50 shows:
   - Anthracnose (rarest, 89 instances): mAP50=0.7865 (not worst)
   - Leaf Spot (dominant, 1365 instances): mAP50=0.7419 (near-worst, worst recall)
   - The bottleneck is NOT the rare class; it is the dominant class with poor recall
   - The 15x imbalance narrative may be wrong or misleading

2. **"copy_paste helps by addressing rare-class imbalance"** — If this were true, Anthracnose should be the worst class. It is not. The actual mechanism may be different.

3. **State of Affairs says "Per-class mAP50 is unavailable"** — REC-3 in system_recommendations.md says per-class mAP50 was never implemented. This is now DONE (evaluate_on_test returns it). The state_of_affairs needs updating.

## Was the State of Affairs accurate?

**Partially accurate but missing critical information:**
- Correctly identified that no per-class mAP data existed
- Correctly identified TTA as non-functional
- Correctly identified 3 dead ends (TTA, imgsz=832 fine-tuning, pretrained=)
- **Wrong** about the bottleneck being rare-class imbalance — the data shows the opposite
- **Wrong** about copy_paste mechanism — the rare-class oversampling theory doesn't match the per-class data
- **Missing** any mention of Angular Leafspot, which is the worst-performing class

## What would you do differently with more or different context?

1. **Run confusion matrix analysis** — Need per-class confusion matrix to understand WHY Leaf Spot recall is 0.5711. Is it confused with Gray Mold? Are lesions too small? This would immediately identify the fix.

2. **Get instance counts per class in test set** — To understand whether mAP50 is weighted by frequency or uniformly averaged across classes. If uniformly averaged, improving any one class helps equally.

3. **Run EXP-6 to completion** — The TTA question is high-value and was not answered.

4. **Check if there are existing per-class experiments** — Did any prior agent run copy_paste=0.55 or 0.6 and capture per-class mAP50? The gen002 experiment suggestions had EXP-4 for this but it doesn't appear to have been run.

5. **Look at actual images** — Are Leaf Spot lesions small? Are they visually similar to Gray Mold? This requires reading the dataset or running an analysis script.

## Specific experiments to run

1. **EXP-3b: Confusion matrix analysis** — Run `model.val()` with `plots=True` to get confusion matrix. Identify which classes Leaf Spot is confused with. This is the single most important diagnostic.

2. **EXP-4 repeat: copy_paste mapping with per-class measurement** — Run copy_paste=0.55 and 0.6 BUT measure per-class mAP50, not just aggregate. The question is not "does aggregate mAP50 improve" but "does Leaf Spot mAP50 improve."

3. **EXP-6 (rerun): TTA on fresh model** — Train a fresh model (can be yolo11n for speed, 20 epochs), then compare TTA vs non-TTA on the SAME model checkpoint. Must complete this time.

4. **Angular Leafspot investigation** — Why is this class worst? It was never mentioned in any prior report. Look at training instances, visual characteristics, annotation quality.

5. **Leaf Spot resolution test** — Train at 640 vs 832 and compare ONLY Leaf Spot mAP50. If Leaf Spot lesions are small, higher resolution might disproportionately help this class.

## What surprised you?

1. **Leaf Spot is the bottleneck, not Anthracnose** — The entire search was predicated on "15x class imbalance → rare classes are the problem." The data shows the opposite: the most common class has the worst recall.

2. **Angular Leafspot is completely unstudied** — It is the worst-performing class at mAP50=0.7201 and was never mentioned in any strategic document, experiment plan, or recommendation. The entire search has been ignoring it.

3. **Blossom Blight has perfect recall (1.0)** — The model over-predicts Blossom Blight. This suggests the class has distinctive visual features that are easy to detect but the model is over-confident.

4. **The state_of_affairs is stale on per-class metrics** — REC-3 in system_recommendations.md says "per-class mAP was never implemented" as a P0 fix needed. But `evaluate_on_test()` in helpers/core.py ALREADY returns per_class metrics. Either REC-3 was written before this was added, or no one has actually used it yet.

## Helper tools feedback

- `evaluate_on_test()` works correctly and returns full per_class block with mAP50, precision, recall per class. The docstring is accurate.
- `train_and_eval()` works but is slow for quick experiments. The GPU lock means all evaluations are serialized — this is correct behavior but limits how many experiments can be run in parallel.
- **Issue**: Running `python3 -c "from helpers.core import ..."` from the wrong venv fails silently (it tries to import ultralytics from system Python, which isn't installed). The evaluate.py re-execs into the correct venv automatically, but direct script invocation requires manually using `/home/sasha/Desktop/idea_evolve/first_project/venv/bin/python`.

## Time budget

**Had ~25 minutes of research agent time:**
- ~5 min: Reading state_of_affairs, description.md, evaluate.py, helpers/core.py
- ~2 min: Running EXP-3 (per-class extraction) — completed successfully
- ~18 min: Running EXP-6 (fresh training + TTA eval) — **INTERRUPTED by timeout**

**What I would do with more time:**
1. Complete EXP-6 (TTA validation) — takes ~9 minutes for 20-epoch training + 2 evals
2. Run confusion matrix analysis on exp5 model
3. Check existing papers/summaries for any relevant prior art
4. Investigate Angular Leafspot — the worst-performing class that no one has studied
