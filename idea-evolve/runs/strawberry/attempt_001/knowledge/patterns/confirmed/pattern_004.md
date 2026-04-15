---
type: pattern
id: pattern_004
name: "Fine-tuning at different resolution destroys domain adaptation"
lifecycle: confirmed
confidence: 0.9
first_seen: gen_002
evidence: [sol_003]
related_ideas: [idea_002, idea_010]
tags: [resolution, fine-tuning, domain-adaptation, regression]
---

Fine-tuning a converged checkpoint at a different resolution (832) from its training resolution (640) for only 20 epochs causes SEVERE performance regression. The domain-adapted model (exp5 at 640) achieves 0.7876 zero-shot at 832, but after 20 epochs of fine-tuning at 832, the score drops to 0.5453 — a loss of 0.24 mAP50. The val-test gap also widens dramatically (0.36 vs the usual 0.10).

This is not merely a limitation — it is active harm. The model's learned resolution-specific features are disrupted before the new resolution features can be established, resulting in worse-than-baseline performance.

The implication: resolution changes during fine-tuning require either from-scratch training (50+ epochs) or staged approaches like progressive resizing.
