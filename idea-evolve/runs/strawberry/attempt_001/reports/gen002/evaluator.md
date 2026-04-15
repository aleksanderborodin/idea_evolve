# Evaluator Report — Generation 2

## Strategic Shift

**strategic_shift: false**

Gen-2 did not produce a score above gen-1 best (0.8328). However, the research findings fundamentally redirect the search strategy by closing three major directions simultaneously.

---

## 1. What Did I Try

### Score Collection
Collected verified scores from 4 solutions + 2 research experiments:
- **exploit_1 sol01 (0.8087):** yolo11s + exp5 via pretrained= flag, AdamW, TTA
- **exploit_1 sol02 (0.8103):** yolo11n from exp5 directly, AdamW, TTA
- **explore_1 sol01 (0.5453):** imgsz=832 fine-tuning from exp5, AdamW
- **research_1 EXP-1 (0.8271):** exp5 zero-shot evaluation (no fine-tuning)
- **research_1 EXP-2 (0.8271):** TTA on exp5 (non-functional)
- **explore_1 sol02:** NOT EVALUATED (timeout)
- **full_1 sol01:** NOT EVALUATED (evaluation interrupted)

### Analysis
- Analyzed all code, scores, and agent observations
- Identified failure modes and root causes
- Extracted 4 new ideas, updated 3 existing ideas, created 3 new patterns
- Updated 3 clusters (one exhausted, two revised)

### Key Decision: idea_002 (imgsz=832) Status
The imgsz=832 fine-tuning experiment produced a severe regression (0.5453). I chose to mark idea_002 as **disputed** rather than debunked, because:
- The SPECIFIC approach (fine-tuning at different resolution from converged checkpoint) was debunked
- The HYPOTHESIS (imgsz=832 captures small lesions better) may still be valid
- Progressive resizing (idea_006) remains a promising alternative approach
- From-scratch training at 832 (not fine-tuning) could test the hypothesis cleanly

---

## 2. What Information I Lacked

- **Per-class mAP50 breakdown** — I cannot determine which disease classes are driving the aggregate score or which are bottleneck classes. This limits my ability to assess whether improvements target dominant or rare classes.
- **Training curves (per-epoch val mAP)** — I cannot determine whether models at epoch 20 were still improving or had plateaued. This affects whether longer training is likely to help.
- **Complete evaluation for explore_1 sol02 and full_1 sol01** — Two valuable experiments (yolo11s + longer training) remain unevaluated. The most important unanswered question is whether yolo11s benefits from more than 20 epochs.
- **exp5 training config** — I don't know the learning rate schedule, augmentation config, or resolution used during exp5's 100-epoch training. This limits my ability to design optimal fine-tuning strategies.

---

## 3. What Given Facts Might Be Wrong or Outdated

- **"TTA provides ~0.5-2% mAP50 lift"** — WRONG. TTA is completely non-functional with current weights. The model silently reverts to single-scale prediction with zero lift.
- **"yolo11s from exp5 checkpoint — combines the larger model scale with converged strawberry-domain weights"** — MISLEADING. The architecture mismatch (yolo11n weights cannot load into yolo11s via pretrained= flag) makes this combination non-trivial. It requires either manual weight loading with shape transposition or training yolo11s from scratch.
- **"imgsz=832 is a top priority direction"** — PARTIALLY WRONG. The SPECIFIC approach (fine-tuning at 832 from 640-converged checkpoint) was shown to be counterproductive. The direction may still be viable via progressive resizing or from-scratch training.

---

## 4. Was the State of Affairs Accurate?

**Partially.** The State of Affairs correctly identified:
- The val-test gap as a real problem
- The optimizer=auto bug
- copy_paste > 0.5 instability

It was WRONG about:
- TTA being a viable free-lunch improvement
- yolo11s + exp5 via pretrained= being a valid approach
- The imgsz=832 direction as a fine-tuning approach

The coverage matrix was accurate: TTA had zero functional coverage, and this gen confirmed it should stay at zero.

---

## 5. What Would I Do Differently

With more time or different context:

1. **Run EXP-3 (yolo11s from exp5)** — the most important untested combination. yolo11s from COCO at 20ep = 0.8328. yolo11s from exp5 could test whether exp5 domain adaptation provides lift over COCO for the larger model.

2. **Get per-class metrics** — Class-level breakdown would reveal whether improvements are coming from dominant classes (Leaf Spot) or rare classes (Anthracnose). This would fundamentally redirect strategy.

3. **Test progressive resizing (idea_006)** — Given that direct imgsz=832 fine-tuning failed, the staged approach (640→832) is the most promising way to test the resolution hypothesis.

4. **Run yolo11s from COCO at 40+ epochs (non-timeout version)** — The most important unanswered question about the best-performing model (gen-1 best at 0.8328) is whether it benefits from more training.

---

## 6. Specific Experiments to Run

1. **yolo11s from COCO at 40 epochs** — Confirm whether 0.8328 at 20ep is noise or signal. If it holds at 40ep, yolo11s is clearly superior. If it plateaus, the answer is "larger model helps up to a point."

2. **Progressive resizing (idea_006)** — 20 epochs at 640, then 10 epochs at 832. Preserves domain knowledge while testing resolution hypothesis.

3. **Per-class mAP50 extraction** — Add per-class metrics to evaluate.py. Currently only aggregate mAP50 is returned. Knowing which classes are limiting the score would redirect the entire search.

4. **yolo11s from exp5 (EXP-3)** — Load yolo11s weights, then manually transfer yolo11n→yolo11s weights where shapes match. Or train yolo11s from scratch with exp5-like augmentation config.

5. **Class-weighted copy_paste** — Upweight rare classes (Anthracnose, Blossom Blight) in copy_paste selection. If class imbalance is the bottleneck, this could provide significant lift.

---

## 7. What Surprised Me

- **TTA was completely non-functional** — Not just ineffective, but silently reverted to single-scale with zero lift. This closes an entire evaluation-improvement direction.

- **Fine-tuning at different resolution was so destructive** — Going from 0.7876 (exp5 zero-shot at 832) to 0.5453 after fine-tuning represents a catastrophic loss. I did not expect the domain disruption to be this severe.

- **Zero-shot exp5 nearly matches best fine-tuned result** — 0.8271 vs 0.8328 (+0.0057 only). In the 20-epoch proxy regime, fine-tuning is essentially neutral. This changes the strategic calculus: we can't expect incremental fine-tuning to reach 0.92+.

- **Architecture mismatch via pretrained= flag** — I assumed Ultralytics would do shape adaptation. The wholesale weight replacement without validation was unexpected.

---

## 8. Helper Tools Feedback

**What worked:**
- `train_and_eval` from helpers.core.py works correctly
- `WEIGHTS_EXP5`, `DATA_V1`, `RUN_DIR` all correct and accessible
- GPU lock mechanism works correctly — no conflicts in parallel evaluation

**What didn't work or was missing:**
- `evaluate_on_test` doesn't support `augment=True` — should be documented
- `model_name` is NOT a valid kwarg for `train_and_eval` — misleading error if passed
- `PROXY_EPOCHS_SCRATCH = 50` conflicts with documented epoch constraints (should be 40 max per constraints.md)

**What I wished existed:**
- Per-class mAP50 extraction in the evaluation output
- Training curve logging (per-epoch val mAP) that survives cleanup
- A way to resume interrupted evaluations without losing the trained weights

---

## 9. Time Budget

**Had enough time for:** Full analysis of 4 scored solutions, 2 research experiments, all agent reports, and comprehensive knowledge file updates.

**Did NOT have time for:** Running evaluate.py on explore_1 sol02 and full_1 sol01 (both timed out before I could evaluate them). These represent real experimental work that produced no scored result.

**If I had more time:** I would have attempted to evaluate explore_1 sol02 manually to get the yolo11s 40-epoch data point. The yolo11s + longer training question is the most important unanswered one, and having even one additional data point would significantly improve the coverage matrix.
