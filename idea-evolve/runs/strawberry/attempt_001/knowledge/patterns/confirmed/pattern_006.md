---
type: pattern
id: pattern_006
name: "20-epoch fine-tuning regime is exhausted for exp5 starting point"
lifecycle: confirmed
confidence: 0.9
first_seen: gen_002
evidence: [sol_001, sol_004, sol_005]
related_ideas: [idea_007, idea_012]
tags: [fine-tuning, marginal-benefit, proxy-regime]
---

Across gen-1 and gen-2, every attempt to fine-tune from the exp5 converged checkpoint for 20 epochs has produced scores at or below the gen-0 nano baseline (~0.8137):
- full_1 (gen_1): 0.8137 with optimizer bug (lr0 ignored)
- exploit_1 sol02 (gen_2): 0.8103 with correct AdamW
- Zero-shot exp5: 0.8271 (no fine-tuning at all)

The best result from exp5 fine-tuning is 0.8137 (below zero-shot). The 20-epoch proxy regime is insufficient for additional fine-tuning to provide positive transfer from a converged 100-epoch checkpoint. The model is already at its asymptotic performance — additional epochs only adapt to val split characteristics without improving test generalization.

This means future experiments should NOT expect incremental gains from continuing to fine-tune exp5 in the 20-epoch regime. Architectural changes (yolo11s from COCO, larger models) and training-from-scratch approaches provide more potential than fine-tuning continuity.
