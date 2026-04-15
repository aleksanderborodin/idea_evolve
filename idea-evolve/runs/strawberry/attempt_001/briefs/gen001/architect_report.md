# Architect Report — Generation 1

## Confidence: High

Cold start is well-structured. Prior experiments give a clear picture of what works and what doesn't. The two-track strategy (explore larger model + refine copy_paste) is sound.

## Data Anomalies

None expected — this is a clean cold start with no prior idea-evolve solutions.

## What Didn't Fit

- **Larger model exploration was limited to yolo11s.** The next generation could explore yolo11m if yolo11s shows promise, but starting conservatively makes sense.
- **copy_paste_mode="mixup" untested.** If copy_paste tuning shows improvement, mixup mode is a natural follow-up for explore_2 in a future gen.
- **Class-weighted loss never mentioned in prior experiments.** research_1 should flag this as a potential direction if TTA/ensemble don't seem promising.

## Strategic Risks

1. **All agents use the same 20-epoch fine-tune budget.** If yolo11s needs more epochs to converge (different model scale), the proxy metric will understate its potential. Mitigation: the description says yolo11s at batch=8 is fine for RTX 5060 Ti. If eval shows yolo11s at only 0.87 vs yolo11n at 0.90, it might just need more epochs.

2. **GPU serialization.** Strawberry requires GPU lock — all agents run sequentially. 4 agents × ~4 min = ~16 min wall-clock for this generation. Acceptable.

3. **research_1 output quality.** If the research report is vague or describes techniques that don't transfer to YOLO instance segmentation, future generations won't benefit. Mitigation: brief asks for "actionable approaches" and "implementation details."

## Open Questions for System Critic

1. **Proxy metric calibration.** The 20-epoch fine-tune from exp5 gives test mAP50 ~0.90. But prior experiments' 50-epoch proxy showed val mAP50 ~0.868 for copy_paste=0.5 while actual 100-epoch val was 0.945. Is the proxy reliable for comparing yolo11s vs yolo11n, or only for ranking copy_paste variants?

2. **When to switch to from-scratch training.** If explore agents consistently plateau below target (0.92), when should we trigger a from-scratch (50 epoch) run vs continuing fine-tune exploration?