# Research Findings — Gen 3 Research 1: Per-Class Bottleneck Analysis + TTA

## Summary

EXP-3 (per-class mAP50 extraction) completed successfully, revealing that the bottleneck classes are **Angular Leafspot** (mAP50=0.7201) and **Leaf Spot** (mAP50=0.7419), not the rare classes as previously assumed. The aggregate mAP50 of 0.8271 is dragged down by these two mid-frequency classes, while rare classes like Anthracnose (0.7865) and Blossom Blight (0.8503) are not the limiting factor. EXP-6 (TTA on fresh training) was interrupted by a timeout and did not complete.

---

## Finding 1: Angular Leafspot and Leaf Spot Are the Actual Bottlenecks

**Relevance**: All solution agents; directly changes prioritization
**Detail**: Per-class mAP50 on exp5 zero-shot model (743 test images):

| Class | mAP50 | Precision | Recall | Frequency |
|-------|-------|-----------|--------|-----------|
| Angular Leafspot | 0.7201 | 0.8011 | 0.6943 | mid |
| Leaf Spot | 0.7419 | 0.8517 | 0.5711 | **dominant** (1365 instances) |
| Anthracnose Fruit Rot | 0.7865 | 0.7384 | 0.7302 | **rarest** (89 instances) |
| Powdery Mildew Fruit | 0.8441 | 0.9003 | 0.7008 | mid |
| Blossom Blight | 0.8503 | 0.7416 | 1.0000 | rare |
| Powdery Mildew Leaf | 0.9181 | 0.8250 | 0.8776 | mid |
| Gray Mold | 0.9289 | 0.8589 | 0.9051 | common |

**Key surprises:**
1. **Leaf Spot (dominant class, 1365 instances) has only 0.7419 mAP50 and worst recall (0.5711)** — despite having 15x more training data than Anthracnose. This is NOT a rare-class problem.
2. **Angular Leafspot is the worst performer at 0.7201 mAP50** — this class was not on anyone's radar.
3. **Anthracnose (rarest, 89 instances) is middle-of-pack at 0.7865** — class imbalance is not the direct bottleneck as assumed.
4. **Blossom Blight has perfect recall (1.000) but precision of only 0.7416** — it detects everything but has false positives.
5. **Gray Mold is best at 0.9289** — consistent with being a common, visually distinctive class.

**Actionable implication**: The assumption that rare-class augmentation (copy_paste targeting Anthracnose) is the top priority is WRONG. Angular Leafspot and Leaf Spot need targeted investigation. Possible reasons for Leaf Spot's poor recall despite high instance count:
- Leaf Spot may have high visual similarity to Gray Mold or other classes → confusion
- Lesions may be small and missed at 640 resolution
- The class may need higher resolution or different augmentation

**Next step**: Agents should investigate WHY Leaf Spot recall is 0.5711 despite 1365 instances. Check confusion matrices if available.

---

## Finding 2: Leaf Spot's Low Recall (0.5711) Is the Single Biggest Lever

**Relevance**: All agents; changes what to optimize
**Detail**: Leaf Spot accounts for the most instances in the dataset and has the worst recall. Improving Leaf Spot recall from 0.57 to 0.75 (matching Gray Mold's 0.91) would be the single largest improvement to aggregate mAP50.

The aggregate mAP50 formula averages across classes. Leaf Spot's low score drags down the mean significantly since it has the most instances.

**Actionable implication**: copy_paste should be re-tuned to oversample Angular Leafspot and Leaf Spot specifically, not Anthracnose. Or, augmentation strategies that improve small lesion detection (e.g., higher resolution, perspective transforms) should target these classes.

---

## Finding 3: Blossom Blight Has 100% Recall but Low Precision (0.7416)

**Relevance**: Exploit agents, tuning for F1
**Detail**: Blossom Blight detects everything (recall=1.0) but has significant false positives (precision=0.7416). This is the opposite problem from Leaf Spot. The model is over-predicting Blossom Blight.

**Actionable implication**: For Blossom Blight, focus on precision improvements (stricter conf thresholds, NMS tuning). Do NOT add more Blossom Blight augmentation.

---

## Finding 4: TTA Status Unknown — EXP-6 Did Not Complete

**Relevance**: All agents doing evaluation
**Detail**: EXP-6 (train fresh yolo11s from COCO → test TTA vs non-TTA on same model) was running at timeout. The experiment was interrupted before producing results.

Prior state: TTA was shown to be non-functional with exp5 weights (zero lift). Whether TTA works on freshly trained models remains **completely unknown**.

**Actionable implication**: Do NOT rely on TTA for evaluations until EXP-6 is rerun and completed. Continue evaluating without TTA.

---

## Finding 5: The Copy-Paste Ceiling May Be a Leaf Spot Problem

**Relevance**: Agents using copy_paste, exploit agents
**Detail**: copy_paste=0.5 was the winning strategy in exp5 (val mAP50=0.945). The assumption was that it helps by oversampling rare classes. But per-class data shows:
- Anthracnose (rarest): mAP50=0.7865 (middle performance)
- Leaf Spot (most common): mAP50=0.7419 (near-bottom performance)

If copy_paste primarily helped Leaf Spot (by duplicating its instances to balance the dataset), then increasing copy_paste would primarily help the already-dominant class, not the rare ones. This contradicts the assumption that copy_paste helps via rare-class oversampling.

**Actionable implication**: The true mechanism behind copy_paste's success may be different from assumed. Rather than targeting rare classes, copy_paste may be helping by providing more Leaf Spot training signal. Further copy_paste increases should be tested specifically for Leaf Spot mAP50 improvement.

---

## Open Questions

1. **Why does Leaf Spot have 0.5711 recall despite 1365 instances?** Possible causes: class confusion (Leaf Spot vs Gray Mold), small lesion size, annotation quality issues. Requires confusion matrix analysis.

2. **Why does Angular Leafspot have the lowest mAP50 (0.7201)?** This class was not mentioned in any prior experiment or recommendation. It is the blind spot of the entire search so far.

3. **Would increasing copy_paste above 0.5 help Leaf Spot specifically?** The mechanism may be different from the assumed rare-class oversampling. This needs per-class mAP50 measurements at different copy_paste values.

4. **Does TTA work with freshly trained models?** EXP-6 did not complete. This is the highest-value single experiment for evaluation efficiency.

5. **What is the confusion matrix between Leaf Spot and Gray Mold?** The low recall on Leaf Spot (0.5711) and high recall on Gray Mold (0.9051) suggests possible confusion between these two classes, which are both leaf-based fungal diseases.
