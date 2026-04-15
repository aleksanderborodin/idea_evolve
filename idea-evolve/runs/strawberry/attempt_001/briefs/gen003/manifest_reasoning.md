# Manifest Reasoning — Generation 3

## Situation Assessment

**Score trajectory:** Plateaued. Gen 1 best = 0.8328. Gen 2 best = 0.8328 (no improvement).
**Generation count:** 3 (early stage — plenty of search space remaining).
**Diversity:** Low. Most attempts cluster around yolo11s/nano from COCO or exp5 fine-tuning. Three major directions closed in gen 2 (TTA, imgsz=832 fine-tune, yolo11s+exp5 via pretrained=).
**Strategic context:** Gen 2 was a strategic redirection that closed 3 major directions simultaneously. The best result remains gen 1's yolo11s from COCO at 20 epochs (0.8328). Gen 2's best was 0.8103 (exploit_1) — below gen 1's baseline.

## What I'm Doing This Generation

### 5 agents total — within 3-8 budget

**Track A — Directed exploitation (exploit_1):**
- `exploit_1`: Refine the gen-1 best (yolo11s from COCO at 20ep=0.8328) with 40 epochs. The most important unanswered question is whether yolo11s was still improving at 20 epochs or plateaued. This is the single highest-value experiment in the system.

**Track B — Radical exploration (explore_1, explore_2, research_1):**
- `explore_1`: Progressive resizing (640→832). This is the only remaining resolution hypothesis. Direct 832 fine-tuning failed catastrophically (0.5453), but progressive resizing may preserve domain while testing the resolution thesis.
- `explore_2`: copy_paste stability ceiling mapping (0.55/0.6). The class imbalance (15x) suggests copy_paste > 0.5 might help rare classes. 0.5 is safe, 0.65 crashes. Map the ceiling.
- `research_1`: TTA fresh-training validation + per-class mAP extraction. TTA was debunked with exp5 (zero lift, silent revert), but may work with a freshly trained model. Per-class mAP is P0 — without it, all search is guesswork.

**System improvement (experimentator_1):**
- `experimentator_1`: Implement per-class mAP in evaluate_on_test() (REC-3 P0). This is not a solution experiment — it's infrastructure that enables all future improvement strategies. Also run the per-class bottleneck experiment on exp5.

## Why This Mix

**exploit_1** (yolo11s 40ep): Highest priority experiment from experiment_suggestions/gen002.md. The 0.8328 baseline is unconfirmed — only 1 data point. This generation MUST answer whether longer training helps.

**explore_1** (progressive resizing): The imgsz=832 hypothesis is the #1 unexplored direction. Direct fine-tuning was catastrophic (0.5453), but progressive resizing is a clean test of whether resolution matters. Different enough from exploit_1 to count as genuine exploration.

**explore_2** (copy_paste mapping): Orthogonal to model-scale exploration. This is about augmentation strategy, not model size. Tests a specific hypothesis about the 15x class imbalance being addressable via copy_paste ceiling.

**research_1** (TTA + per-class): Low-cost experiments (1 min + 9 min). TTA revalidation is quick closure of a direction that wasted planning in gen 1-2. Per-class mAP is the highest-value diagnostic we can get.

**experimentator_1** (per-class infrastructure): REC-3 is marked P0 by the system critic. Every agent report cited missing per-class data as their #1 information gap. Building this infrastructure enables targeted improvements in gen 4+.

## What I'm NOT Doing This Generation

- **Genetic crossover**: No good parent pairs identified. The population has one strong result (yolo11s 0.8328) and everything else is worse. Crossing weak solutions won't help.
- **TTA as primary direction**: TTA was debunked on exp5 (zero lift). Only testing if fresh training enables it — not pursuing it as a primary strategy.
- **yolo11s+exp5 via pretrained=**: Debunked — architecture mismatch.
- **imgsz=832 direct fine-tuning**: Debunked — catastrophic regression.
- **Full agents (from scratch training)**: Gen 2 full_1 consumed 75+ minutes and timed out. 50-epoch runs are unreliable in the current infrastructure. Stick to 20-40 epoch range.

## Timeout Selection

- **explore_1 (progressive resizing):** 1200s — two-stage training with 832 fine-tuning may hit memory limits. Needs room to fail gracefully.
- **explore_2 (copy_paste mapping):** 1200s — two separate 20-epoch runs. Fast but need buffer for sequential execution.
- **exploit_1 (yolo11s 40ep):** 900s — single 40-epoch run should complete in ~7-8 min. Less complex than explore_1.
- **research_1 (TTA + per-class):** 600s — quick experiments, low risk.
- **experimentator_1 (per-class implementation):** 1200s — code modification + testing. Needs time to write, validate, and test the updated evaluate_on_test().

## Risks

1. **Progressive resizing may OOM at 832**: batch=8 at 832 resolution is memory-intensive. Fallback plan is to evaluate stage 1 at 640.
2. **yolo11s 40ep may plateau below 0.8328**: If this happens, the baseline is confirmed and more exploration is needed.
3. **experimentator_1 changes helpers/core.py incorrectly**: Could break evaluate.py for all future generations. Must validate carefully.
4. **copy_paste=0.6 may crash**: If both explore_2 runs crash, the ceiling is below 0.6 and we'd need to know this for all future augmentation planning.

## Expected Outcomes

- **Best case:** yolo11s 40ep exceeds 0.8328 → scale up to yolo11m or 60 epochs; progressive resizing works → scale resolution further.
- **Expected:** yolo11s 40ep ≈ 0.8328 (plateau confirmed), progressive resizing inconclusive, copy_paste ceiling between 0.55-0.65, per-class data reveals bottleneck class.
- **Worst case:** yolo11s 40ep < 0.8328 (overfitting), explore_1 OOMs, explore_2 crashes both. Still get per-class data to redirect search.