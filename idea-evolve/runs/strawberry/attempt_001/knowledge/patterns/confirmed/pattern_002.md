---
type: pattern
id: pattern_002
name: "copy_paste=0.65 causes broken pipe crashes"
lifecycle: confirmed
confidence: 0.8
first_seen: gen_001
evidence: [sol_003]
related_ideas: [idea_004]
tags: [copy-paste, crash, instability]
---

copy_paste=0.65 caused training to crash with `[Errno 32] Broken pipe` error during evaluation. The training process was killed or crashed before completion, producing an invalid solution (is_valid=0). This is the first observed failure at high copy_paste values. The safe upper bound appears to be below 0.65.
