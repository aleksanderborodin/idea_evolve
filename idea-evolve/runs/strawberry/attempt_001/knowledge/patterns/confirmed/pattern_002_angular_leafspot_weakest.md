---
type: pattern
id: pattern_002
name: "Angular Leafspot is consistently the weakest class"
lifecycle: confirmed
confidence: 0.9
first_seen: gen_001
evidence: ["gen001_explore_1_sol02", "gen001_explore_1_sol03", "gen001_explore_1_sol04", "gen001_explore_1_sol05", "gen001_full_1_sol01", "gen001_full_1_sol02"]
related_ideas: []
tags: ["per-class", "weak-class", "angular-leafspot"]
---

## Pattern

Angular Leafspot mAP50 consistently falls in the 0.66-0.74 range across all gen001 solutions — the lowest of all 7 disease classes.

## Per-class mAP50 from best solution (gen001_explore_1_sol04, mAP50=0.8296):

| Class | mAP50 | Notes |
|-------|-------|-------|
| Angular Leafspot | 0.7444 | WORST — consistent across all |
| Anthracnose Fruit Rot | 0.8577 | Improved with mixup |
| Blossom Blight | 0.8386 | Perfect recall (1.0) in most |
| Gray Mold | 0.909 | Strongest class |
| Leaf Spot | 0.760 | Second weakest |
| Powdery Mildew Fruit | 0.777 | Mid-range |
| Powdery Mildew Leaf | 0.9201 | Second strongest |

## Implication

Angular Leafspot and Leaf Spot are the bottleneck classes. Improving performance on these two classes would have the highest impact on overall mAP50. No gen001 solution significantly improved Angular Leafspot despite targeting it.