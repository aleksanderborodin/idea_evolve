# Manifest Reasoning — Generation 2

## Situation Assessment

Gen 1 established a clean baseline. Best score: 0.8328 (yolo11s from COCO, 20 epochs). The yolo11s model outperformed nano at the same epoch count (+0.015). Fine-tuning from exp5 for 20 epochs was neutral (0.8137 = gen-0 baseline) — likely because 20 epochs is too short for positive transfer from a converged checkpoint.

Key open questions that Gen 2 must resolve:
1. Does yolo11s + exp5 + proper optimizer outperform yolo11s + COCO? (The best combo is untested)
2. Does imgsz=832 close the val-test gap? (0.10 gap suggests test lesions may be smaller)
3. Is yolo11s from COPO at 50 epochs significantly better than at 20 epochs?
4. Does TTA provide a free lift on the best model?

## Agent Mix

**4 agents total** — balanced between exploitation and radical exploration.

### research_1 (Track B — mandatory research)
- Runs EXP-1 (zero-shot exp5) + EXP-2 (TTA on best model) — 30-60 seconds total
- These experiments are the highest information-gain per cost in the entire pipeline
- Zero-shot exp5 determines whether fine-tuning from exp5 is useful at all
- TTA establishes whether all future scores should use augmented evaluation

### exploit_1 (Track A — directed exploitation)
- Combines yolo11s + exp5 + AdamW + TTA into one solution
- This is the most logical next step: best model scale + converged checkpoint + fixed optimizer + TTA
- If this works (≥ 0.85), the path forward is clear
- If it fails (≤ 0.82), the 20-epoch fine-tune regime is the bottleneck

### explore_1 (Track B — radical exploration, resolution hypothesis)
- Tests imgsz=832 from exp5 with yolo11s
- The val-test gap (0.10) is the strongest signal in the data — higher resolution might close it
- This is a genuinely different direction that exploit_1 (same model, different resolution)

### full_1 (Track B — from-scratch yolo11s validation)
- Runs yolo11s from COCO for 50 epochs
- Validates whether the larger model genuinely needs more epochs to show its potential
- If 50 epochs from COCO gets val > 0.90, yolo11s is the right model family
- If still ~0.83, the problem is the from-scratch regime, not the model scale

## What I Deliberately Did NOT Include

- **copy_paste exploration (0.55, 0.6)** — covered by REC-7 in system recommendations, but gen 1 explore_2's crash at 0.65 suggests the ceiling is near 0.5. Filler experiments in a saturated direction.
- **yolo11m or larger** — yolo11s already showed gains at 20 epochs. Going bigger without validating yolo11s+exp5 first would be premature.
- **Progressive resizing (640→832)** — would compound two variables. Test flat 832 first.
- **Experimentator for REC-1 (optimizer fix)** — the exploit_1 agent will use explicit optimizer='AdamW', which serves as the fix. No separate experimentator needed.
- **More than 4 agents** — GPU lock serializes all strawberry agents. 4 × ~7 min = ~28 min wall-clock. Budget discipline.

## Timeout Choices

Based on gen 1 timing:
- research_1: 600s (just evaluation, no training — will finish in < 5 min)
- exploit_1: 1500s (training + TTA eval, may need wrap-up)
- explore_1: 1200s (training at larger images, slightly slower)
- full_1: 1800s (50 epochs from scratch — longest training mode)

## Risks

1. **GPU serialization bottleneck**: All 4 agents run sequentially. If one times out, the next waits. 28 min minimum wall-clock for this generation.
2. **TTA not in helpers**: research_1 must implement TTA manually. If the implementation is wrong, EXP-2 produces garbage.
3. **imgsz=832 may OOM**: yolo11s at 832px with batch=8 might exceed RTX 5060 Ti memory. May need batch=4 or 6.
4. **yolo11s from COCO at 50 epochs**: If it crashes (CUDA OOM), full_1 produces nothing. No fallback.

## Strategic Risks If This Generation Fails

- If exploit_1 (yolo11s+exp5) scores ≤ 0.82, the 20-epoch fine-tune regime may be fundamentally limited. May need to trigger 50-epoch from-scratch runs earlier.
- If all 4 agents produce < 0.84, the proxy metric may be miscalibrated and the actual 100-epoch performance is much better than proxy suggests.
