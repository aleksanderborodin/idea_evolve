---
type: pattern
id: pattern_005
name: "TTA silently non-functional — no warning in metrics"
lifecycle: confirmed
confidence: 0.95
first_seen: gen_002
evidence: [sol_006]
related_ideas: [idea_003, idea_011]
tags: [tta, evaluation, non-functional, silent-failure]
---

Test-Time Augmentation (augment=True) is completely non-functional with the exp5 best.pt checkpoint. Ultralytics prints a warning ("Model does not support 'augment=True', reverting to single-scale prediction") but the returned metrics show the same mAP50 as without TTA (0.8271 in both cases). There is no error, no exception, and no indication in the metrics themselves that TTA was not applied.

The silent fallback is dangerous because:
1. An agent implementing TTA believes they are getting a free boost
2. The metrics don't reveal that TTA was not applied
3. The only signal is a console warning that might be missed

The fix requires retraining a model that supports TTA, or investigating why the exp5 export disabled TTA.
