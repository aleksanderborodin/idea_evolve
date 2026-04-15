---
type: pattern
id: pattern_003
name: "20-epoch fine-tune from exp5 shows val-test gap"
lifecycle: confirmed
confidence: 0.8
first_seen: gen_001
evidence: [sol_001]
related_ideas: [idea_007]
tags: [val-test-gap, fine-tuning, proxy]
---

Fine-tuning from the exp5 checkpoint (100-epoch converged) for 20 epochs produces a large val-test gap: val mAP50=0.91 but test mAP50=0.8137 — a 0.10 gap. The val split improves dramatically during fine-tuning but the test split only marginally matches the baseline. This suggests 20 epochs is too short for positive transfer, or the fine-tuning is adapting to val distribution without generalizing.
