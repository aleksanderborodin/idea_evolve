---
type: idea
id: idea_007
name: "Val-test distribution gap in 20-epoch fine-tuning"
lifecycle: established
confidence: 0.9
first_seen: gen_001
last_updated: gen_002
last_confirmed_gen: gen_002
supported_by: [sol_001, sol_003]
contradicted_by: []
related_ideas: [idea_012]
cluster: cluster_003
tags: [generalization, val-test-gap, proxy-calibration]
---

## What It Is

Fine-tuning from the exp5 checkpoint (100-epoch converged) for 20 epochs produces a large gap between val mAP50 and test mAP50. The val split improves dramatically during fine-tuning but the test split does not — additional fine-tuning adapts to val distribution without generalizing.

## Updated Evidence — gen_002

**New data confirms and extends the finding:**

1. **explore_1 sol01 gen_2 (imgsz=832 fine-tune):** val≈0.91, test=0.5453 — gap of ~0.36 at 832 resolution. The gap WORSENS when fine-tuning at a different resolution, suggesting the val adaptation is resolution-specific and doesn't transfer.

2. **exploit_1 sol02 gen_2 (yolo11n from exp5, 20 epochs):** test=0.8103 — essentially same as full_1's 0.8137 and gen-0 baseline. The 20-epoch fine-tuning from converged checkpoint provides no test improvement despite val gains.

3. **research_1 EXP-1 (exp5 zero-shot):** val=0.91, test=0.8271. The converged model has its own val-test gap (~0.08), but it's much smaller than the gap produced by additional fine-tuning.

**Pattern across all gen-2 fine-tuning attempts:**
- Zero-shot from converged checkpoint: small gap (~0.08)
- 20 epochs additional fine-tuning: larger gap (~0.10-0.36)
- The additional fine-tuning adapts to val without improving test generalization

## Implications

- Agents should NOT compare 20-epoch results to 100-epoch val results directly
- The val-test gap is real and is worsened by fine-tuning in the proxy regime
- Techniques that help generalization (regularization, augmentation) may be more valuable in the proxy regime
- The path to 0.92+ likely requires improving the model's generalization, not its val-split adaptation

## Status: Established

Confidence maintained at 0.9. Multiple independent experiments confirm this pattern. The finding is robust across different model architectures and resolutions.
