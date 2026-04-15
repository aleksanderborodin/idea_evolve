## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen001/explore_1/sol01.py` → mAP50 = 0.8328 (yolo11s from COCO, 20 epochs)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/population/gen002/exploit_1/sol02.py` → mAP50 = 0.8103

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/knowledge/state_of_affairs.md` — Layer 0 strategic overview
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/feedback/system_recommendations.md` — REC-3: implement per-class mAP in evaluate_on_test() — P0 priority
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/feedback/experiment_suggestions/gen002.md` — EXP-3: per-class mAP extraction
- `problems/strawberry/description.md` — Available helpers (train_and_eval, evaluate_on_test)
- `problems/strawberry/helpers/core.py` — Current evaluate_on_test() implementation

## Directive
**You have ONE specific question to answer and ONE tool to build.**

### Question: Is the 15x class imbalance the actual bottleneck?
The coverage matrix and state of affairs repeatedly cite the 15x class imbalance (Leaf Spot 1365 vs Anthracnose 89) as a likely bottleneck. But we have zero per-class mAP data to confirm this. Without it, every improvement strategy is guesswork.

**Experiment:**
Run `evaluate_on_test(WEIGHTS_EXP5, save_per_class=True)` and extract per-class mAP50, precision, and recall for all 7 disease classes.

**Deliverable:** Write findings to `output/per_class_findings.md`:
- Table: disease name | mAP50 | recall | precision | instances in train
- Rank classes worst-first by mAP50
- Identify which classes are limiting the aggregate (bottleneck classes)
- State whether class-weighted augmentation should be the top priority

### ALSO: Implement per-class mAP in evaluate_on_test() (REC-3 P0)

The system recommendation REC-3 says: modify `evaluate_on_test()` in `helpers/core.py` to return per-class precision, recall, and mAP50.

The current `evaluate_on_test()` only returns aggregate mAP50. This is insufficient — all agents are flying blind on which disease classes are driving the aggregate score.

**Implementation:**
Modify `helpers/core.py` `evaluate_on_test()` to return:
```python
return {
    "mAP50": round(float(m.seg.map50), 4),
    "mAP50_95": round(float(m.seg.map), 4),
    "per_class": {
        "precision": [float(x) for x in m.seg.cp],
        "recall": [float(x) for x in m.seg.cr],
        "mAP50": [float(x) for x in m.seg.ap50],
    }
}
```

Also write the per-class data to `LAST_PER_CLASS_METRICS` as JSON so agents can inspect it without re-running.

**IMPORTANT:** Write the modified `evaluate_on_test()` to `output/helpers/core_update.py` so the orchestrator can validate it and deploy it. Do NOT modify `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/strawberry/attempt_001/problem/helpers/core.py` directly — the orchestrator validates and deploys.

After writing, test that the updated function works correctly by running the per-class experiment above.

**This is a mandatory fix.** Without per-class metrics, the entire search is blind to the most likely bottleneck (rare-class underperformance in the 15x imbalanced dataset).