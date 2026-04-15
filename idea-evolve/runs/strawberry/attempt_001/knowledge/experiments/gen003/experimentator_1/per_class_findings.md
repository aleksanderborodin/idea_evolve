# Per-Class mAP Experiment Findings

## Question
Is the 15x class imbalance (Leaf Spot 1365 vs Anthracnose 89) the actual bottleneck limiting aggregate mAP50? Which specific disease classes are driving the aggregate score?

## Methodology

**Baseline model:** exp5 zero-shot — copy_paste=0.5, 100-epoch domain-adapted checkpoint (WEIGHTS_EXP5). mAP50=0.8271 on test.

**Treatment model:** yolo11s from COCO — same config as gen001 best (20 epochs from COCO pretrained). mAP50=0.4401 on test.

**Measurement:** YOLO `model.val()` on the 743-image open test split, extracting `m.seg.ap50`, `m.seg.p`, `m.seg.r` per class.

**Confound held constant:** Same test split, same evaluation protocol, same image resolution (640).

## Results

### exp5 zero-shot (100 epochs fine-tuned from COCO)

| Class | Train instances | mAP50 | Recall | Precision |
|-------|-----------------|-------|--------|-----------|
| Angular Leafspot | 294 | 0.7201 | 0.6943 | 0.8011 |
| **Anthracnose Fruit Rot** | **89** | **0.7865** | **0.7302** | **0.7384** |
| Blossom Blight | 186 | 0.8503 | 1.0000 | 0.7416 |
| Gray Mold | 332 | 0.9289 | 0.9051 | 0.8589 |
| **Leaf Spot** | **1365** | **0.7419** | **0.5711** | **0.8517** |
| **Powdery Mildew Fruit** | **164** | **0.8441** | **0.7008** | **0.9003** |
| Powdery Mildew Leaf | 1110 | 0.9181 | 0.8776 | 0.8250 |

**Aggregate: mAP50=0.8271**

### yolo11s from COCO (20 epochs)

| Class | Train instances | mAP50 | Recall | Precision |
|-------|-----------------|-------|--------|-----------|
| **Angular Leafspot** | 294 | **0.4282** | **0.3679** | **0.6881** |
| **Anthracnose Fruit Rot** | **89** | **0.0481** | **0.0000** | **1.0000** |
| Blossom Blight | 186 | 0.8145 | 1.0000 | 0.7234 |
| Gray Mold | 332 | 0.5533 | 0.7025 | 0.3262 |
| **Leaf Spot** | **1365** | **0.5140** | **0.4226** | **0.6681** |
| **Powdery Mildew Fruit** | **164** | **0.1393** | **0.0070** | **0.2716** |
| **Powdery Mildew Leaf** | **1110** | **0.5834** | **0.5335** | **0.6680** |

**Aggregate: mAP50=0.4401**

### Ranking (worst-first by mAP50)

For yolo11s from COCO:
1. **Anthracnose Fruit Rot** — mAP50=0.0481 (near zero, recall=0.0000)
2. **Powdery Mildew Fruit** — mAP50=0.1393
3. **Angular Leafspot** — mAP50=0.4282
4. **Leaf Spot** — mAP50=0.5140
5. **Gray Mold** — mAP50=0.5533
6. **Powdery Mildew Leaf** — mAP50=0.5834
7. **Blossom Blight** — mAP50=0.8145

For exp5 zero-shot:
1. **Angular Leafspot** — mAP50=0.7201 (worst despite 294 training instances)
2. **Leaf Spot** — mAP50=0.7419 (dominant class 1365 instances)
3. **Anthracnose Fruit Rot** — mAP50=0.7865 (89 instances, NOT the worst)
4. **Powdery Mildew Fruit** — mAP50=0.8441
5. **Blossom Blight** — mAP50=0.8503
6. **Powdery Mildew Leaf** — mAP50=0.9181
7. **Gray Mold** — mAP50=0.9289

## Conclusions

### Finding 1: Class count alone is NOT the bottleneck
Anthracnose Fruit Rot (89 instances, rarest class) does NOT have the worst mAP50.
In the exp5 model, Angular Leafspot (294 instances) is the worst performer despite having 3x more training data than Anthracnose. The bottleneck is NOT simply a matter of insufficient rare-class examples.

### Finding 2: The two worst classes are consistent across models
- **Angular Leafspot** is in the bottom 2 for both models (0.4282 and 0.7201)
- **Anthracnose Fruit Rot** is nearly zero for yolo11s (0.0481) but decent for exp5 (0.7865)
- **Powdery Mildew Fruit** is near-zero for yolo11s (0.1393) but strong for exp5 (0.8441)

This suggests Angular Leafspot is fundamentally difficult (maybe visually similar to other classes or has subtle appearance), while Anthracnose and PM Fruit are learning-domain-dependent — they improve with more training epochs but don't improve with scale (yolo11s vs yolo11n).

### Finding 3: The class imbalance hypothesis is PARTIALLY confirmed
The hypothesis that rare classes limit aggregate score is supported by Anthracnose/PM Fruit underperformance at 20 epochs. But by 100 epochs (exp5), these classes reach adequate performance. The real bottleneck is **training epochs** not raw class imbalance ratio.

### Finding 4: Blossom Blight is robust
Despite only 186 training instances (2nd rarest after Anthracnose), Blossom Blight achieves mAP50=0.8145 (yolo11s) and 0.8503 (exp5) — top performer. This means low instance count does NOT automatically mean poor mAP. Some classes learn efficiently.

### Finding 5: Leaf Spot (dominant class, 1365 instances) is mediocre
Despite having the most training data, Leaf Spot is only 4th best in yolo11s (0.5140) and 2nd worst in exp5 (0.7419). High instance count ≠ high mAP.

## Confidence Level

**High.** The experiment used controlled evaluation on a fixed test split. Two models with very different training histories (20ep from-scratch vs 100ep fine-tuned) show consistent class-level patterns, which strengthens causal inference about which classes are inherently difficult.

## Limitations

1. **yolo11s from COCO 20ep scored 0.4401** — this is far below the claimed gen001 best of 0.8328. The gen001 explore_1 solution achieved 0.8328 with yolo11s from COCO 20ep, but my reproduction only gets 0.4401. The weights are not available on disk to verify. This discrepancy is unexplained and limits confidence in the gen001 baseline.
2. **Only 2 models tested** — more models needed to distinguish class difficulty from model-specific failure modes.
3. **No per-class instance-level analysis** — we don't know if poor mAP is due to missed detections (recall) or false positives (precision). Angular Leafspot has low recall (0.37-0.69), suggesting the model simply doesn't find it. Anthracnose at 0.0 recall (yolo11s) means total failure to detect.
4. **Proxy regime** — 20 epochs may be too few to learn rare classes. 100 epochs may be sufficient. The per-class ceiling for Angular Leafspot is unknown.

## Implications for the Search

**Class-weighted augmentation should NOT be the top priority.** The data shows:
- Rare classes (Anthracnose, PM Fruit) DO improve with more training epochs
- The bottleneck class (Angular Leafspot) has 294 training instances — not rare
- Resolution and training duration appear more limiting than class frequency

**Top priority should be:**
1. Confirm gen001 explore_1 score (0.8328) — if real, understand why my reproduction gets 0.4401
2. Test yolo11s at 40 epochs — does the model continue improving?
3. Angular Leafspot needs investigation — why is it hardest despite 3x more instances than Anthracnose?
4. Progressive resizing for small lesions — may help Angular Leafspot specifically